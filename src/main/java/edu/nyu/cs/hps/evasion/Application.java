package edu.nyu.cs.hps.evasion;

import edu.nyu.cs.hps.evasion.game.GameHost;

public class Application {
  public static void main(String[] args) {
    if(args.length != 4){
      System.err.println("Require args: [player 1 port] [player 2 port] [max walls] [wall placement delay]");
    } else {
      try {
        GameHost.hostGame(Integer.parseInt(args[0]), Integer.parseInt(args[1]), Integer.parseInt(args[2]), Integer.parseInt(args[3]));
      }
      catch (Exception e) {
        System.err.println(e.getMessage());
      }
    }
  }
}
