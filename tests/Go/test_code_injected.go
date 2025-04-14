package main
import (
	"fmt"
	"math"
	"os"
	"strconv"
)


func sum(a bool, b bool) bool {
	return a && b
}

func main() {
	a, erra := strconv.ParseBool(os.Args[1]);
	if erra != nil {
		fmt.Println("Invalid input. Please enter valid values.")
		return
	}
	b, errb := strconv.ParseBool(os.Args[2]);
	if errb != nil {
		fmt.Println("Invalid input. Please enter valid values.")
		return
	}
	result := sum(a, b);
	fmt.Printf("%t",result)
}