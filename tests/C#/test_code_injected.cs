using System;
using System.Text.Json;
using System.Collections.Generic;
using System.Collections.Generic;
using System.Linq;
class Program
{
	public static float SumNestedFloatList(List<List<float>> nestedList)
    {
        float total = 0;

        foreach (var innerList in nestedList)
        {
            foreach (var number in innerList)
            {
                total += number;
            }
        }

        return total;
    }

static void Main(string[] args)
	{
	List<List<float>> b = JsonSerializer.Deserialize<List<List<float>>>(args[1]);
	var result = SumNestedFloatList(b);
	Console.WriteLine(result);
}
}