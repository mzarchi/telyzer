use iced::Task;

#[derive(Debug, Clone, Default)]
pub struct LoginApp {
    pub phone: String,
    pub error: Option<String>,
}

#[derive(Debug, Clone)]
pub enum Message {
    PhoneChanged(String),
    LoginPressed,
    LoginResult(Result<(), String>),
}

impl LoginApp {
    pub fn update(&mut self, message: Message) -> Task<Message> {
        match message {
            Message::PhoneChanged(phone) => {
                self.phone = phone;
                Task::none()
            }
            Message::LoginPressed => {
                self.error = None;

                let phone = self.phone.clone();
                Task::perform(
                    async move {
                        if phone.is_empty() {
                            Err("Phone number cannot be empty".to_string())
                        } else {
                            Ok(())
                        }
                    },
                    Message::LoginResult,
                )
            }
            Message::LoginResult(result) => {
                match result {
                    Ok(_) => {}
                    Err(e) => {
                        self.error = Some(e);
                    }
                }
                Task::none()
            }
        }
    }
}
