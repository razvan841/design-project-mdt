import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class parse{

    public static <T> List<?> parseNestedArray(String input, Function<String, T> converter) {
        input = input.trim();

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
                    List<T> flat = new ArrayList<>();
                    for (String num : input.split(",")) {
                        flat.add(converter.apply(num.trim()));
                    }
                    return flat;
                }
            }
        }
        return result;
    }

    private static <T> List<T> parseList(String input, Function<String, T> converter) {
        input = input.trim();

        if (!input.startsWith("[") || !input.endsWith("]")) {
            throw new IllegalArgumentException("Invalid list format.");
        }

        input = input.substring(1, input.length() - 1).trim();

        List<T> list = new ArrayList<>();
        StringBuilder numberToken = new StringBuilder();

        for (int i = 0; i < input.length(); i++) {
            char c = input.charAt(i);
            if (c == ',' || c == ']') {
                if (numberToken.length() > 0) {
                    list.add(converter.apply(numberToken.toString().trim()));
                    numberToken.setLength(0);
                }
            } else {
                numberToken.append(c);
            }
        }

        if (numberToken.length() > 0) {
            list.add(converter.apply(numberToken.toString().trim()));
        }

        return list;
    }
}
