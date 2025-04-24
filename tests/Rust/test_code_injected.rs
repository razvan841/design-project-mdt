use std::env;

use serde_json::Value;
fn sum(a: i64, b: i64) -> i64 {
    a + b
}

fn main() {
	let args: Vec<String> = env::args().collect();


	let a: Vec<String> = serde_json::from_str(&args[1]).expect("Expected a different type!");;
	let b: Vec<bool> = serde_json::from_str(&args[2]).expect("Expected a different type!");;
	let result = sum(a, b);
	println!("{}", result);
}