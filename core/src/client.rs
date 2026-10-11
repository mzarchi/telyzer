use crate::config::Paths;
use crate::error::{CoreError, Result};
use crate::secrets::{API_ID};
use grammers_client::Client;
use grammers_mtsender::SenderPool;
use grammers_session::storages::SqliteSession;
use std::sync::Arc;

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

        let SenderPool { runner, handle, .. } =
            SenderPool::new(Arc::clone(&session), API_ID);

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