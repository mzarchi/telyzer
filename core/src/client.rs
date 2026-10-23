use crate::config::Paths;
use crate::error::{CoreError, Result};
use crate::secrets::API_ID;
use grammers_client::Client;
use grammers_mtsender::{ConnectionParams, SenderPool};
use grammers_session::storages::SqliteSession;
use std::sync::Arc;
use tokio::task::JoinHandle;

const APP_VERSION: &str = concat!("v", env!("CARGO_PKG_VERSION"));
const DEVICE_MODEL: &str = "Telyzer Desktop";
const SYSTEM_LANG_CODE: &str = "en";
const LANG_CODE: &str = "en";

/// A single connection to Telegram. Create it once and share it by reference.
/// Call [`TelyzerClient::shutdown`] when done so the background task ends
/// and the session database is released.
pub struct TelyzerClient {
    client: Client,
    // Asks the sender pool to stop. Stored as a closure so this struct does not
    // depend on the exact handle type grammers returns from `SenderPool`.
    quit: Box<dyn FnOnce() + Send>,
    runner: JoinHandle<()>,
}

impl TelyzerClient {
    pub async fn new(paths: &Paths) -> Result<Self> {
        let session_path = paths.prepare_session_file()?;

        let session = Arc::new(
            SqliteSession::open(&session_path)
                .await
                .map_err(|e| CoreError::CorruptedSession(e.to_string()))?,
        );

        let params = ConnectionParams {
            device_model: DEVICE_MODEL.to_string(),
            system_version: std::env::consts::OS.to_string(),
            app_version: APP_VERSION.to_string(),
            system_lang_code: SYSTEM_LANG_CODE.to_string(),
            lang_code: LANG_CODE.to_string(),
            ..Default::default()
        };

        let SenderPool { runner, handle, .. } =
            SenderPool::with_configuration(session, API_ID, params);

        let client = Client::new(handle.clone());
        let runner = tokio::spawn(runner.run());
        let quit: Box<dyn FnOnce() + Send> = Box::new(move || {
            drop(handle);
        });

        Ok(Self {
            client,
            quit,
            runner,
        })
    }

    pub fn inner(&self) -> &Client {
        &self.client
    }

    pub async fn is_authorized(&self) -> Result<bool> {
        Ok(self.client.is_authorized().await?)
    }

    /// Stops the network task and waits until it has finished, which releases
    /// the SQLite session so its files can be safely deleted afterwards.
    pub async fn shutdown(self) {
        (self.quit)();
        let _ = self.runner.await;
    }
}
