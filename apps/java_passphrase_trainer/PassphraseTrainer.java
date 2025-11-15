import java.security.SecureRandom;
import java.util.*;

public class PassphraseTrainer {
  static String[] words = {"river","mango","cloud","piano","temple","print","violet","ladder","curry","garden"};
  static String specials = "!@#";

  public static void main(String[] args){
    Scanner sc = new Scanner(System.in);
    System.out.print("Pick 3 favorite simple words (space separated): ");
    String[] fav = sc.nextLine().trim().toLowerCase().split("\\s+");
    List<String> base = new ArrayList<>(Arrays.asList(fav));
    SecureRandom rnd = new SecureRandom();

    // ensure at least 3 words
    while(base.size() < 3) {
      base.add(words[rnd.nextInt(words.length)]);
    }

    String pass = base.get(0)
            + base.get(1).substring(0,1).toUpperCase()
            + base.get(1).substring(1)
            + base.get(2)
            + (rnd.nextInt(89)+10)  // 2-digit number 10–99
            + specials.charAt(rnd.nextInt(specials.length()));

    int bits = (int)Math.round(Math.log(words.length)/Math.log(2))*3 + 7; // rough entropy estimate

    System.out.println("Try this style (do NOT reuse exactly): " + pass + "  ~"+bits+" bits.");
    System.out.println("Rule 1: never reuse the same passphrase on different sites.");
    System.out.println("Rule 2: put real accounts (email/bank) into a password manager, not on paper.");
  }
}
