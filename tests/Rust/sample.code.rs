use std::env;

fn sum(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let args: Vec<String> = env::args().collect();

    let a: i32 = match args[1].parse() {
        Ok(num) => num,
        Err(_) => {
            eprintln!("Error: '{}' is not a valid integer", args[1]);
            std::process::exit(1);
        }
    };

    let b: i32 = match args[2].parse() {
        Ok(num) => num,
        Err(_) => {
            eprintln!("Error: '{}' is not a valid integer", args[2]);
            std::process::exit(1);
        }
    };

    let result = sum(a, b);
    println!(result);
}
