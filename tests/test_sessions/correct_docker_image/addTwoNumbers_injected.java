import java.util.Arrays;

@SuppressWarnings("unchecked")
 public class addTwoNumbers_injected {
	public static void main(String[] args) {


	int x0;
	int x1;
	int result;
	x0 = Integer.parseInt(args[0]);
	x1 = Integer.parseInt(args[1]);
	result = addTwoNumbers(x0, x1);
	System.out.println(result);

}
public static int addTwoNumbers(int a, int b) {
	int[] numbers = {a, b};
	Arrays.sort(numbers);
	return numbers[0] + numbers[1];
}
}
