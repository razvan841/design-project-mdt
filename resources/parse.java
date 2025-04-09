
// This file is part of the Modular Differential Testing Project.

// The Modular Differential Testing Project is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// The Modular Differential Testing Project is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with the source code. If not, see <https://www.gnu.org/licenses/>.

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class parse{

    public static <T> List<?> parseNestedArray(String input, Function<String, T> converter) {

        if (input.startsWith("'") && input.endsWith("'")) {
            input = input.substring(1, input.length() - 1).trim();
        }

        if (!input.startsWith("[") || !input.endsWith("]")) {
            throw new IllegalArgumentException("Input must be a bracketed list.");
        }

        input = input.substring(1, input.length() - 1).trim();
        List<Object> result = new ArrayList<>();

        int bracketCount = 0;
        int tokenStart = 0;

        for (int i = 0; i < input.length(); i++) {
            char c = input.charAt(i);

            if (c == '[') {
                if (bracketCount == 0) tokenStart = i;
                bracketCount++;
            } else if (c == ']') {
                bracketCount--;
                if (bracketCount == 0) {

                    String sub = input.substring(tokenStart, i + 1);
                    result.add(parseNestedArray(sub, converter));
                }
            } else if (bracketCount == 0 && c != ',') {
                int end = input.indexOf(',', i);
                if (end == -1) end = input.length();
                String value = input.substring(i, end).trim();
                if (!value.isEmpty()) {
                    result.add(converter.apply(value));
                }
                i = end - 1;
            }
        }

        return result;
    }
}
