use thiserror::Error;

#[derive(Debug, Error)]
pub enum CoreError {
    #[error("Could not determine project directories for this platform")]
    ProjectDirsUnavailable,

    #[error("Failed to create directory at {path}: {source}")]
    CreateDir {
        path: String,
        #[source]
        source: std::io::Error,
    },

    #[error("Failed to create file at {path}: {source}")]
    CreateFile {
        path: String,
        #[source]
        source: std::io::Error,
    },

    #[error("Failed to set permissions on {path}: {source}")]
    SetPermissions {
        path: String,
        #[source]
        source: std::io::Error,
    },

    #[error("Failed to delete {path}: {source}")]
    RemoveFile {
        path: String,
        #[source]
        source: std::io::Error,
    },

    #[error("Session file is corrupted or invalid: {0}")]
    CorruptedSession(String),

    #[error("Phone number must be in international format, e.g. +989121234567")]
    InvalidPhone,

    #[error("Telegram error: {0}")]
    Telegram(#[from] grammers_client::InvocationError),

    #[error("Sign-in error: {0}")]
    SignIn(Box<grammers_client::SignInError>),
}

pub type Result<T> = std::result::Result<T, CoreError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn project_dirs_message() {
        assert_eq!(
            CoreError::ProjectDirsUnavailable.to_string(),
            "Could not determine project directories for this platform"
        );
    }

    #[test]
    fn invalid_phone_message_mentions_international_format() {
        assert!(CoreError::InvalidPhone
            .to_string()
            .contains("international"));
    }

    #[test]
    fn corrupted_session_includes_reason() {
        let e = CoreError::CorruptedSession("bad header".into());
        assert!(e.to_string().contains("bad header"));
    }

    #[test]
    fn io_errors_include_path() {
        let e = CoreError::RemoveFile {
            path: "/tmp/x".into(),
            source: std::io::Error::from(std::io::ErrorKind::PermissionDenied),
        };
        assert!(e.to_string().contains("/tmp/x"));
    }
}
