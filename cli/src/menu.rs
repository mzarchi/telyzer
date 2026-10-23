use anyhow::Result;
use dialoguer::{theme::ColorfulTheme, Select};
use telyzer_core::{Paths, TelyzerClient};

use crate::commands;

const VERSION: &str = env!("CARGO_PKG_VERSION");

enum MenuAction {
    Login,
    AccountInfo,
    Contacts,
    Channels,
    Groups,
    Bots,
    Logout,
    Exit,
}

pub async fn run(paths: &Paths, mut client: TelyzerClient) -> Result<()> {
    loop {
        println!("Telyzer (CLI) v{VERSION}");

        let is_auth = client.is_authorized().await?;
        if is_auth {
            if let Ok(me) = client.get_me().await {
                println!("Hey {}!", me.first_name().unwrap_or("User"));
            }
        } else {
            println!("Status: Not logged in");
        }

        let actions: Vec<(MenuAction, &str)> = if is_auth {
            vec![
                (MenuAction::AccountInfo, "My Account Info"),
                (MenuAction::Contacts, "Contacts"),
                (MenuAction::Channels, "Channels"),
                (MenuAction::Groups, "Groups"),
                (MenuAction::Bots, "Bots"),
                (MenuAction::Logout, "Logout"),
                (MenuAction::Exit, "Exit app"),
            ]
        } else {
            vec![(MenuAction::Login, "Login"), (MenuAction::Exit, "Exit app")]
        };

        let items: Vec<&str> = actions.iter().map(|(_, label)| *label).collect();

        let theme = ColorfulTheme {
            prompt_prefix: dialoguer::console::style(String::new()),
            active_item_prefix: dialoguer::console::style(String::from("    ❯")),
            inactive_item_prefix: dialoguer::console::style(String::from("     ")),
            ..ColorfulTheme::default()
        };

        let selection = Select::with_theme(&theme)
            .with_prompt("    Choose an action")
            .items(&items)
            .default(0)
            .interact()?;

        match actions[selection].0 {
            MenuAction::Login => {
                if let Err(e) = commands::login::run(&client).await {
                    eprintln!("Error: {e}");
                }
            }
            MenuAction::AccountInfo => {
                if let Err(e) = commands::whoami::run(&client).await {
                    eprintln!("Error: {e}");
                }
            }
            MenuAction::Contacts => println!("Contacts list is not implemented yet."),
            MenuAction::Channels => println!("Channels list is not implemented yet."),
            MenuAction::Groups => println!("Groups list is not implemented yet."),
            MenuAction::Bots => println!("Bots list is not implemented yet."),
            MenuAction::Logout => {
                // logout consumes the client; a fresh one is created afterwards
                if let Err(e) = commands::logout::run(client, paths).await {
                    eprintln!("Error: {e}");
                }
                client = TelyzerClient::new(paths).await?;
            }
            MenuAction::Exit => {
                println!("Exiting app...");
                client.shutdown().await;
                break;
            }
        }

        println!();
        println!("Press Enter to continue...");
        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
    }

    Ok(())
}
