using System;
using System.Collections.Generic;
using System.Linq;
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