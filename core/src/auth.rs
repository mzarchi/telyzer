use crate::client::TelyzerClient;
use crate::error::{CoreError, Result};
use crate::secrets::API_HASH;
use grammers_client::client::{LoginToken, PasswordToken, SignInError};
use grammers_client::peer::User;

#[derive(Debug)]
pub enum SignInResult {
    Success(Box<User>),
    NeedPassword(PasswordToken),
    InvalidCode,
}

/// Normalizes a phone number (strips spaces, dashes, parentheses) and checks
/// it looks like `+` followed by 8-15 digits.
pub fn validate_phone(input: &str) -> Result<String> {
    let cleaned: String = input
        .chars()
        .filter(|c| !matches!(c, ' ' | '-' | '(' | ')'))
        .collect();

    let digits = cleaned.strip_prefix('+').ok_or(CoreError::InvalidPhone)?;

    if (8..=15).contains(&digits.len()) && digits.chars().all(|c| c.is_ascii_digit()) {
        Ok(cleaned)
    } else {
        Err(CoreError::InvalidPhone)
    }
}

impl TelyzerClient {
    pub async fn request_login_code(&self, phone: &str) -> Result<LoginToken> {
        let token = self.inner().request_login_code(phone, API_HASH).await?;
        Ok(token)
    }

    pub async fn sign_in(&self, token: &LoginToken, code: &str) -> Result<SignInResult> {
        match self.inner().sign_in(token, code).await {
            Ok(user) => Ok(SignInResult::Success(Box::new(user))),
            Err(SignInError::PasswordRequired(password_token)) => {
                Ok(SignInResult::NeedPassword(password_token))
            }
            Err(SignInError::InvalidCode) => Ok(SignInResult::InvalidCode),
            Err(e) => Err(CoreError::SignIn(Box::new(e))),
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
            .map_err(|e| CoreError::SignIn(Box::new(e)))?;
        Ok(user)
    }

    pub async fn get_me(&self) -> Result<User> {
        let me = self.inner().get_me().await?;
        Ok(me)
    }

    pub async fn sign_out(&self) -> Result<()> {
        self.inner().sign_out().await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_valid_international_number() {
        assert_eq!(validate_phone("+989121234567").unwrap(), "+989121234567");
    }

    #[test]
    fn strips_formatting_characters() {
        assert_eq!(
            validate_phone(" +98 (912) 123-4567 ").unwrap(),
            "+989121234567"
        );
    }

    #[test]
    fn rejects_missing_plus() {
        assert!(validate_phone("989121234567").is_err());
    }

    #[test]
    fn rejects_empty_input() {
        assert!(validate_phone("").is_err());
        assert!(validate_phone("   ").is_err());
    }

    #[test]
    fn rejects_non_digits() {
        assert!(validate_phone("+98912abc4567").is_err());
    }

    #[test]
    fn rejects_too_short_and_too_long() {
        assert!(validate_phone("+1234567").is_err());
        assert!(validate_phone("+1234567890123456").is_err());
    }
}
