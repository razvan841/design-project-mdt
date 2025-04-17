function sum(a: number, b: number): number {
    return a + b;
}

function main() {
    const args = process.argv.slice(2);

    const a = parseInt(args[2], 10);
    const b = parseInt(args[3], 10);
    const result = sum(a, b);
    console.log(result);
}