use crate::config::Paths;
use crate::error::{CoreError, Result};
use crate::secrets::API_ID;
use grammers_client::Client;
use grammers_mtsender::{ConnectionParams, SenderPool};
use grammers_session::storages::SqliteSession;
use std::sync::Arc;

const APP_VERSION: &str = "vC120-2610";
const DEVICE_MODEL: &str = "Telyzer Desktop";
const SYSTEM_VERSION: &str = "Windows";
const SYSTEM_LANG_CODE: &str = "en";
const LANG_CODE: &str = "en";

#[derive(Clone)]
pub struct TelyzerClient {
    client: Client,
    #[allow(dead_code)]
    session: Arc<SqliteSession>,
}

impl TelyzerClient {
    pub async fn new(paths: &Paths) -> Result<Self> {
        let session_path = paths.session_file();

        let session = Arc::new(
            SqliteSession::open(&session_path)
                .await
                .map_err(|e| CoreError::CorruptedSession(e.to_string()))?,
        );

        // ساخت پارامترهای اتصال با اطلاعات خودمون
        let params = ConnectionParams {
            device_model: DEVICE_MODEL.to_string(),
            system_version: SYSTEM_VERSION.to_string(),
            app_version: APP_VERSION.to_string(),
            system_lang_code: SYSTEM_LANG_CODE.to_string(),
            lang_code: LANG_CODE.to_string(),
            ..Default::default()
        };

        let SenderPool { runner, handle, .. } =
            SenderPool::with_configuration(Arc::clone(&session), API_ID, params);

        let client = Client::new(handle);
        tokio::spawn(runner.run());

        Ok(Self { client, session })
    }

    pub fn inner(&self) -> &Client {
        &self.client
    }

    pub async fn is_authorized(&self) -> Result<bool> {
        Ok(self.client.is_authorized().await?)
    }
}