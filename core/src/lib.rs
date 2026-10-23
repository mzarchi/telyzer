pub mod auth;
pub mod client;
pub mod config;
pub mod error;
mod secrets;

pub use auth::{validate_phone, SignInResult};
pub use client::TelyzerClient;
pub use config::Paths;
pub use error::{CoreError, Result};
