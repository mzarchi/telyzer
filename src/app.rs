use crate::constants::*;

#[derive(Default)]
pub struct LoginApp {
    pub phone: String,
    pub error: Option<String>,
}

impl LoginApp {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn try_login(&mut self) {
        if self.phone.trim().is_empty() {
            self.error = Some(ENTER_PHONE_NUMBER.into());
            return;
        }
        self.error = None;
        println!("Phone: {}", self.phone);
    }
}