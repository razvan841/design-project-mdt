package main

import (
	"fmt"
	"math"
	"os"
	"strconv"
)

// power calculates base^exp
func power(base float64, exp float64) float64 {
	return math.Pow(base, exp)
}

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: go run main.go <base> <exponent>")
		return
	}

	// Convert command-line arguments to float64
	base, err1 := strconv.ParseFloat(os.Args[1], 64)
	exp, err2 := strconv.ParseFloat(os.Args[2], 64)
	if err1 != nil || err2 != nil {
		fmt.Println("Error: Please provide valid numbers for base and exponent.")
		return
	}

	// Calculate and print result
	result := power(base, exp)
	fmt.Printf("%f^%f = %f\n", base, exp, result)
}
