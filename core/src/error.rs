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

    #[error("Failed to read session file at {path}: {source}")]
    ReadSession {
        path: String,
        #[source]
        source: std::io::Error,
    },

    #[error("Session file is corrupted or invalid: {0}")]
    CorruptedSession(String),

    #[error("Login failed: {0}")]
    LoginFailed(String),

    #[error("Telegram error: {0}")]
    Telegram(#[from] grammers_client::InvocationError),

    #[error("Sign-in error: {0}")]
    SignIn(Box<grammers_client::SignInError>),

    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
}

pub type Result<T> = std::result::Result<T, CoreError>;
