#[derive(Default)]
pub struct LoginApp {
    pub phone: String,
    pub error: Option<String>,
}

#[derive(Debug, Clone)]
pub enum Message {
    PhoneChanged(String),
    LoginPressed,
}

impl LoginApp {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn update(&mut self, message: Message) {
        match message {
            Message::PhoneChanged(value) => {
                self.phone = value;
                self.error = None;
            }
            Message::LoginPressed => {
                if self.phone.trim().is_empty() {
                    self.error = Some("Please enter a phone number".into());
                } else {
                    self.error = None;
                    println!("Phone: {}", self.phone);
                }
            }
        }
    }
}
