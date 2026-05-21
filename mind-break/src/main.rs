use std::io::{self, Write};

fn main() {
    println!("Welcome to Mind Break!");
    println!("You define the secret number, then try to guess it.");

    let secret = loop {
        let input = prompt("Enter the secret number (3 to 10 digits, positive integer): ");
        match validate_number(&input) {
            Ok(()) => break input,
            Err(msg) => eprintln!("Invalid secret number: {msg}"),
        }
    };

    let max_attempts = loop {
        let input = prompt("Max attempts? Press Enter for unlimited: ");
        if input.trim().is_empty() {
            break None;
        }

        match input.trim().parse::<u32>() {
            Ok(value) if value > 0 => break Some(value),
            _ => eprintln!("Please enter a positive integer or just press Enter for unlimited."),
        }
    };

    println!(
        "\nGame started! Try to guess the {}-digit number.",
        secret.len()
    );

    let mut attempts = 0_u32;

    loop {
        if let Some(limit) = max_attempts {
            if attempts >= limit {
                println!("\nNo attempts left. You lost!");
                println!("Secret number was: {secret}");
                break;
            }
        }

        let guess = prompt("Enter your guess: ");

        if guess.len() != secret.len() {
            eprintln!("Guess must be exactly {} digits long.", secret.len());
            continue;
        }

        if !guess.chars().all(|c| c.is_ascii_digit()) {
            eprintln!("Guess must contain digits only.");
            continue;
        }

        attempts += 1;

        let (correct_position, wrong_position) = score_guess(&secret, &guess);

        if guess == secret {
            println!("\nCorrect! You guessed the number in {attempts} attempt(s).");
            break;
        }

        println!(
            "Correct position: {correct_position}, correct digit wrong position: {wrong_position}"
        );

        if let Some(limit) = max_attempts {
            println!("Attempts remaining: {}", limit.saturating_sub(attempts));
        }
    }
}

fn prompt(message: &str) -> String {
    print!("{message}");
    io::stdout().flush().expect("failed to flush stdout");

    let mut input = String::new();
    io::stdin()
        .read_line(&mut input)
        .expect("failed to read from stdin");

    input.trim().to_string()
}

fn validate_number(input: &str) -> Result<(), &'static str> {
    if !input.chars().all(|c| c.is_ascii_digit()) {
        return Err("must contain digits only");
    }

    if input.starts_with('0') {
        return Err("must be a positive integer and cannot start with 0");
    }

    if !(3..=10).contains(&input.len()) {
        return Err("length must be between 3 and 10 digits");
    }

    Ok(())
}

fn score_guess(secret: &str, guess: &str) -> (u32, u32) {
    let mut correct_position = 0_u32;
    let mut secret_counts = [0_u32; 10];
    let mut guess_counts = [0_u32; 10];

    for (s, g) in secret.bytes().zip(guess.bytes()) {
        if s == g {
            correct_position += 1;
        }
        secret_counts[(s - b'0') as usize] += 1;
        guess_counts[(g - b'0') as usize] += 1;
    }

    let total_matches: u32 = secret_counts
        .iter()
        .zip(guess_counts.iter())
        .map(|(s, g)| (*s).min(*g))
        .sum();

    let wrong_position = total_matches.saturating_sub(correct_position);

    (correct_position, wrong_position)
}
