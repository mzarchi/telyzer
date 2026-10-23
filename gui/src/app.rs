use iced::Task;
use telyzer_core::validate_phone;

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
                        validate_phone(&phone)
                            .map(|_| ())
                            .map_err(|e| e.to_string())
                    },
                    Message::LoginResult,
                )
            }
            Message::LoginResult(result) => {
                if let Err(e) = result {
                    self.error = Some(e);
                }
                Task::none()
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn phone_changed_updates_state() {
        let mut app = LoginApp::default();
        let _ = app.update(Message::PhoneChanged("+989121234567".into()));
        assert_eq!(app.phone, "+989121234567");
    }

    #[test]
    fn login_pressed_clears_previous_error() {
        let mut app = LoginApp {
            error: Some("old".into()),
            ..Default::default()
        };
        let _ = app.update(Message::LoginPressed);
        assert!(app.error.is_none());
    }

    #[test]
    fn failed_result_sets_error() {
        let mut app = LoginApp::default();
        let _ = app.update(Message::LoginResult(Err("bad".into())));
        assert_eq!(app.error.as_deref(), Some("bad"));
    }

    #[test]
    fn successful_result_keeps_error_empty() {
        let mut app = LoginApp::default();
        let _ = app.update(Message::LoginResult(Ok(())));
        assert!(app.error.is_none());
    }
}
