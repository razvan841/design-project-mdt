function sumInts(a: number, b: number): number {
    return a + b;
}

	const a = parseInt(process.argv[2])
	const b = parseInt(process.argv[3])
	const result = sum(a, b)
	console.log(result)
