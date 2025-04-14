using System;

class Program
{
    // Function to sum two numbers
    static double Sum(double a, double b)
    {
        return a + b;
    }

    // Main function that takes arguments from the command line
    static void Main(string[] args)
    {

        try
        {
            // Convert the arguments to numbers
            double num1 = Convert.ToDouble(args[1]);
            double num2 = Convert.ToDouble(args[2]);

            // Call the sum function
            double result = Sum(num1, num2);

            // Print the result
            Console.WriteLine("The sum is: " + result);
        }
        catch (FormatException)
        {
            Console.WriteLine("Invalid input. Please enter valid numbers.");
        }
    }
}
