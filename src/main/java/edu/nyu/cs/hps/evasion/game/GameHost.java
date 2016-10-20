package edu.nyu.cs.hps.evasion.game;

import java.awt.*;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;

public class GameHost {

  public static void hostGame(int portP1, int portP2, int maxWalls, int wallPlacementDelay) throws Exception {

    System.out.println("Player 1: connect to port " + portP1);
    System.out.println("Player 2: connect to port " + portP2);

    IO io = new IO();
    List<Integer> ports = new ArrayList<>();
    ports.add(portP1);
    ports.add(portP2);
    io.start(ports);

    System.out.println("Starting game.");

    int hunterIndex = 0;
    int preyIndex = 1;
    int gameNum = 0;

    int p1AsPreyScore = 0;
    int p2AsPreyScore = 0;

    int p1Timeouts = 0;
    int p2Timeouts = 0;

    while(gameNum < 2) {
      Duration hunterTime = Duration.ofSeconds(120);
      Duration preyTime = Duration.ofSeconds(120);

      Game game = new Game(maxWalls, wallPlacementDelay);

      io.sendLine(hunterIndex, "hunter");
      io.sendLine(preyIndex, "prey");

      Thread.sleep(1000 / 60);

      boolean hunterTimeout = false;
      boolean preyTimeout = false;
      boolean done = false;
      while (!done) {
        String gameString = gameNum + " " + game.getState().toString();

        Future<IO.Response> hunterResponseFuture = io.getResponse(hunterIndex, hunterTime.toMillis() + " " + gameString);
        Future<IO.Response> preyResponseFuture = io.getResponse(preyIndex, preyTime.toMillis() + " " + gameString);

        IO.Response hunterResponse = null;
        IO.Response preyResponse = null;
        if(hunterTime.minus(preyTime).isNegative()){
          Instant start = Instant.now();
          try {
            hunterResponse = hunterResponseFuture.get(hunterTime.toNanos(), TimeUnit.NANOSECONDS);
          } catch (TimeoutException e) {
            hunterTimeout = true;
          }
          Duration elapsed = Duration.between(start, Instant.now());
          Duration toWait = preyTime.minus(elapsed);
          try {
            preyResponse = preyResponseFuture.get(toWait.toNanos(), TimeUnit.NANOSECONDS);
          } catch (TimeoutException e) {
            preyTimeout = true;
          }
        } else {
          Instant start = Instant.now();
          try {
            preyResponse = preyResponseFuture.get(preyTime.toNanos(), TimeUnit.NANOSECONDS);
          } catch (TimeoutException e) {
            preyTimeout = true;
          }
          Duration elapsed = Duration.between(start, Instant.now());
          Duration toWait = hunterTime.minus(elapsed);
          try {
            hunterResponse = hunterResponseFuture.get(toWait.toNanos(), TimeUnit.NANOSECONDS);
          } catch (TimeoutException e) {
            hunterTimeout = true;
          }
        }

        if(hunterTimeout || preyTimeout) {
          break;
        }

        hunterTime = hunterTime.minus(hunterResponse.elapsed);
        preyTime = preyTime.minus(preyResponse.elapsed);

        hunterTimeout = hunterTime.isNegative();
        preyTimeout = preyTime.isNegative();

        if(hunterTimeout || preyTimeout){
          break;
        }

        Game.WallCreationType hunterWallAction = Game.WallCreationType.NONE;
        List<Integer> hunterWallsToDelete = new ArrayList<>();
        Point preyMovement = new Point(0, 0);

        List<Integer> hunterData = Arrays.stream(hunterResponse.message.split("\\s+"))
          .map(Integer::parseInt)
          .collect(Collectors.toList());

        if(hunterData.get(1) == game.getState().ticknum) {
          if (hunterData.size() >= 3 && hunterData.get(0) == gameNum) {
            if (hunterData.get(2) == 1) {
              hunterWallAction = Game.WallCreationType.HORIZONTAL;
            } else if (hunterData.get(2) == 2) {
              hunterWallAction = Game.WallCreationType.VERTICAL;
            }
            hunterWallsToDelete = hunterData.subList(3, hunterData.size());
          }
        } else {
          System.out.println(io.getName(hunterIndex) + " is lagging; missed tick " + game.getState().ticknum);
        }

        List<Integer> preyData = Arrays.stream(preyResponse.message.split("\\s+"))
          .map(Integer::parseInt)
          .collect(Collectors.toList());
        if(preyData.get(1) == game.getState().ticknum) {
          if (preyData.size() >= 4 && preyData.get(0) == gameNum && preyData.get(1) == game.getState().ticknum) {
            preyMovement.x = preyData.get(2);
            preyMovement.y = preyData.get(3);
          }
        } else {
          System.out.println(io.getName(preyIndex) + " is lagging; missed tick " + game.getState().ticknum);
        }

        done = game.tick(hunterWallAction, hunterWallsToDelete, preyMovement);
      }

      if(preyIndex == 0){
        if(preyTimeout){
          p1Timeouts++;
        } else {
          p1AsPreyScore += game.getState().ticknum;
        }
        if(hunterTimeout){
          p2Timeouts++;
        }
      } else {
        if(preyTimeout){
          p2Timeouts++;
        } else {
          p2AsPreyScore += game.getState().ticknum;
        }
        if(hunterTimeout){
          p1Timeouts++;
        }
      }

      if(hunterTimeout && preyTimeout){
        System.out.println("Both timed out!");
      } else if(hunterTimeout){
        System.out.println(io.getName(hunterIndex) + " timed out!");
      } else if (preyTimeout){
        System.out.println(io.getName(preyIndex) + " timed out!");
      } else {
        System.out.println("Score (hunter=" + io.getName(hunterIndex) + ", prey=" + io.getName(preyIndex) + "): " + game.getState().ticknum);
      }

      hunterIndex = 1-hunterIndex;
      preyIndex = 1-preyIndex;
      gameNum++;

      Thread.sleep(1000 / 60);
    }

    if(p1Timeouts == 0 && p2Timeouts == 0) {
      if (p1AsPreyScore == p2AsPreyScore) {
        System.out.println("Tied! Both = " + p1AsPreyScore);
      }
      String winner = (p1AsPreyScore > p2AsPreyScore) ? io.getName(0) : io.getName(1);
      System.out.println(winner + " wins (" + io.getName(0) + " = " + p1AsPreyScore + ", " + io.getName(1) + " = " + p2AsPreyScore + ")");
    }

    io.sendLine(hunterIndex, "done");
    io.sendLine(preyIndex, "done");

    io.destroy();
  }
}
