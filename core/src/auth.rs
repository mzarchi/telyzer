use crate::client::TelyzerClient;
use crate::error::{CoreError, Result};
use crate::secrets::API_HASH;
use grammers_client::client::{LoginToken, PasswordToken, SignInError};
use grammers_client::peer::User;

#[derive(Debug)]
pub enum SignInResult {
    Success(User),
    NeedPassword(PasswordToken),
}

impl TelyzerClient {
    pub async fn request_login_code(&self, phone: &str) -> Result<LoginToken> {
        let token = self.inner().request_login_code(phone, API_HASH).await?;
        Ok(token)
    }

    pub async fn sign_in(&self, token: &LoginToken, code: &str) -> Result<SignInResult> {
        match self.inner().sign_in(token, code).await {
            Ok(user) => Ok(SignInResult::Success(user)),
            Err(SignInError::PasswordRequired(password_token)) => {
                Ok(SignInResult::NeedPassword(password_token))
            }
            Err(e) => Err(CoreError::LoginFailed(e.to_string())),
        }
    }

    pub async fn sign_in_password(
        &self,
        password_token: PasswordToken,
        password: &str,
    ) -> Result<User> {
        let user = self
            .inner()
            .check_password(password_token, password)
            .await
            .map_err(|e| CoreError::LoginFailed(e.to_string()))?;
        Ok(user)
    }

    pub async fn get_me(&self) -> Result<User> {
        let me = self.inner().get_me().await?;
        Ok(me)
    }
}