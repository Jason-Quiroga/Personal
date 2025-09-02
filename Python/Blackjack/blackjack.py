""" This project is Jason Quiroga's python-created Blackjack! It features fully functional blackjack
with player saving and betting.

Author: Jason Quiroga
Class: CSI-160-03
Assignment: Final Project
Due Date: 12/12/22

Certification of Authenticity:
I certify that this is entirely my own work, except where I have given
fully-documented references to the work of others. I understand the definition
and consequences of plagiarism and acknowledge that the assessor of this
assignment may, for the purpose of assessing this assignment:
- Reproduce this assignment and provide a copy to another member of academic
- staff; and/or Communicate a copy of this assignment to a plagiarism checking
- service (which may then retain a copy of this assignment on its database for
- the purpose of future plagiarism checking)
"""

import random
import time
import colorama

dealer = {"hand": "", "card_value": 0, "play": True}
player = {"hand": "", "card_value": 0, "points": 100, "bet": 0, "winnings": 0, "choice": '', "name": ""}

# Tuple containing a full deck of cards
default_deck = \
    (
        "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣",
        "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
        "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
        "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠"
    )
deck = []
firstTime = True  # Runs the game startup on initial load, then never again.
play = True  # Play is set to "false" when the player stands.


def repopulate_deck():
    """
        If the deck is running low on cards, it will be repopulated with a new deck, keeping the old cards
        to be used first.
    :return: newdeck (list) - The new shuffled deck
    """
    newdeck = list(default_deck)
    random.shuffle(newdeck)
    return newdeck


def val_check(cardplayer):
    """
        Tells if the cardplayer can either keep playing, has busted, or has blackjack.
    :param cardplayer: Either the player or the dealer's dictionary
    :return: Either "bust", "play", or "blackjack", depending on what the cardplayer's card_value is
    (and according to Blackjack rules).
    """
    if cardplayer["card_value"] > 21:
        return "bust"
    elif cardplayer["card_value"] < 21:
        return "play"
    elif cardplayer["card_value"] == 21:
        if cardplayer["hand"].find('A') != -1:
            if cardplayer["hand"].find('J') != -1:
                return "blackjack"
            elif cardplayer["hand"].find('Q') != -1:
                return "blackjack"
            elif cardplayer["hand"].find('K') != -1:
                return "blackjack"
            else:
                return "play"
        else:
            return "play"


def deal(cardplayer):
    """
    Deals a single card to the player
    :param cardplayer: (Dictionary) Either the player or the dealer's dictionary
    :return: The cardplayer's hand plus the new card, and the cardplayer's card values plus the new card's value.
            The function returns two values because it is called twice in the same line.
    """
    card = deck.pop(random.randint(0, len(deck) - 1))

    value = card[0:-1]

    if value.isalpha():  # If the card is a letter (A,J,Q, or K), assign it the appropriate value
        if value == "A":
            if cardplayer["card_value"] + 11 > 21:  # If the player is going to bust with an Ace being 11, make it 1
                value = 1
            else:
                value = 11

        else:
            value = 10
    value = int(value)

    return cardplayer["hand"] + card + " ", cardplayer["card_value"] + value


def player_play(cardplayer):
    """
    Asks the player if they want to hit or stand.
    - If the player hits, it draws them a card from the deal() function, tells them the card they drew, and then
    returns their hand, card values, and choice of either hit or stand
    - If the player stands, the function returns their hand, card values, and choice of either hit or stand.
    - If they enter any other choice besides 's' or 'h', it will repromt them to choose.
    :param cardplayer: (Dictionary) Either the player or the dealer's dictionary
    :return: Hand (string) - New hand with the added cards
            card_value (int) - The new value of cards
            choice (string) - The play's choice of what to do
    """
    print(colorama.Fore.GREEN + "(H)it", colorama.Fore.RESET + "  or  " + colorama.Fore.RED + "(S)tand?: " +
          colorama.Fore.RESET)
    choice = input()
    try:  # If player choice can be made lower, do it. Otherwise, just skip (it's most likely an illegal character)
        choice = choice.lower()
    except:
        pass
    if choice == 'h':
        cardplayer["hand"], cardplayer["card_value"] = deal(cardplayer)
        print(colorama.Fore.GREEN + f"Hit a {cardplayer['hand'][-4:]}" + colorama.Fore.RESET)
        return cardplayer["hand"], cardplayer["card_value"], choice
    elif choice == 's':
        print(colorama.Fore.RED + "Stand" + colorama.Fore.RESET)
        return cardplayer["hand"], cardplayer["card_value"], choice
    else:
        print("Not a valid choice.")
        return cardplayer["hand"], cardplayer["card_value"], ""


def dealer_play(dealerdeck):
    """
    Plays for the dealer when called.
    :param dealerdeck: (Dictionary) the dealer's deck
    :return: hand (string) - The dealer's new hand with the added card
            ddeck (int) - The dealer's new card values
    """
    hand, ddeck = deal(dealerdeck)
    card = hand[-4:]
    print(colorama.Fore.RED + f"Dealer draws {card}, totaling {ddeck}" + colorama.Fore.RESET)
    return hand, ddeck


def calculate_winnings(winner, status):
    """
        Calculates the winnings / losings of the round, then resets the game to allow for replayability.
    :param winner: (string) - Whoever won the round, either "dealer" or "player"
    :param status: (string) - Shows how the player won, either "bj" (blackjack), "tie" for a tie,
                            "win" for a normal win, or "bust" for a bust.
    :return: None
    """
    if winner == 'dealer':
        player["points"] -= player["bet"]
        print(colorama.Fore.LIGHTRED_EX + f"\nDealer wins! You lose {player['bet']} points." + colorama.Fore.RESET +
                                          f" You currently have {player['points']} points.")
    else:
        if status == 'bj':  # Determine if player won through Blackjack or beating the dealer.
            player["winnings"] = player["bet"] * 2
            print(colorama.Fore.MAGENTA + f"\nYou hit a Blackjack! You won {player['winnings']} points!"
                  + colorama.Fore.RESET)
        elif status == 'tie':
            print(colorama.Fore.YELLOW + "\nYou tied. You lose no points." + colorama.Fore.RESET)
        else:
            player["winnings"] = player["bet"] * 1
            print(colorama.Fore.GREEN + f"\nYou win! You won {player['winnings']} points!" + colorama.Fore.RESET)

        player["points"] += int(player["winnings"])
        print(f"You currently have {player['points']} points.")

    # Reset player bets, winnings, hand, choice, and card value
    player["bet"] = 0
    player["winnings"] = 0
    player["hand"] = ""
    player["card_value"] = 0
    player["choice"] = ""

    # Reset dealer hand and card value
    dealer["hand"] = ""
    dealer["card_value"] = 0

    time.sleep(3)


def first_time_setup():
    """
    Runs if the game is just starting. Introduces the player to the game and allows the player to "log in" and
    regain their points if they played previously. If not, it creates an account for them and saves it to the
    file "customers.txt".
    - Also prints the "bard.txt" file, which holds a ~fancy~ welcome for Bard's Casino.
    :return: None
    """
    with open('bard.txt') as f:  # Open and read the file to the variable "bard", then prints the text
        bard = f.read()
    print(colorama.Fore.YELLOW, colorama.Style.BRIGHT, bard)
    print(colorama.Fore.MAGENTA)
    print("Hello! Welcome to the Blackjack table at Bard's Casino!")
    print("Winning pays out 1:1, and blackjacks pay out 2:1.\n")
    print("If you've already played here before, you can get your points back! "
          "Just enter your name that you used previously.", colorama.Fore.RESET)
    player["name"] = input("Will you please tell me your name?")

    customer_file = open("customers.txt", 'r')  # Opens the customers file and assigns it to the customer_file variable
    found = False
    for line in customer_file:
        if line.find(player["name"]) != -1:
            # print(line)
            pointsindex = line.find("-")
            points = line[pointsindex + 2:-1]
            player["points"] = int(points)
            if player["points"] != 0:  # If the player's bankrupt, be merciful and give them 100 points.
                print(f"Welcome back, {player['name']}! You currently have {points} points. Onto the game!")
            else:
                print(f"Welcome back, {player['name']}! You currently have 0 points.")
                print("Bard is merciful and will give you 100 points on the house to play with. Good luck.")
                player["points"] = 100
            found = True
    customer_file.close()
    if found is False:  # If the player is new, add them to customers.txt
        customer_file = open("customers.txt", 'a')
        customer_file.write(f"{player['name']} - 100\n")
        print(f"Nice to meet you, {player['name']}! We'll start you off with 100 points. Onto the game!")
        customer_file.close()
    time.sleep(3)


def bet(cardplayer):
    """
    Allows the player to bet their points. Will also allow the player to exit, and if they do, save their points.
    Will not allow anything other than ENTER or numbers (not 0).
    :param cardplayer: (Dictionary) The player
    :return: cardplayer["bet"] - The player's bet.
    """
    cardplayer["bet"] = input(f"\nYou currently have {cardplayer['points']} points.\nHow much would you like to bet?"
                              f" If you would like to stop, please just press enter.\nPlace Bet / Enter (Exit): ")
    if cardplayer["bet"] == "":
        print(f"\nOk {cardplayer['name']}, we'll save your score for when you return."
              f"\nThank you for playing. See you soon!")
        player_save(cardplayer)
        exit()
    else:
        if not cardplayer["bet"].isdecimal():
            print("Incorrect bet input. Please try again.")
            time.sleep(2)
            cardplayer["bet"] = str(bet(cardplayer))
        if cardplayer["bet"][0] == "0":
            print("Incorrect bet input. Please try again.")
            time.sleep(2)
            cardplayer["bet"] = str(bet(cardplayer))
        if int(cardplayer["bet"]) > int(cardplayer["points"]):
            print("You cannot bet more than you have! Please try again.")
            time.sleep(2)
            cardplayer["bet"] = str(bet(cardplayer))
        cardplayer["bet"] = int(cardplayer["bet"])  # Turn bet from str to int
        return cardplayer["bet"]


def player_save(cardplayer):
    """
    Saves the player's points to the customers.txt file.
    :param cardplayer: (Dictionary) The player
    :return: None
    """
    with open('customers.txt', 'r') as file:
        data = file.readlines()

    counter = 0
    for line in data:
        counter += 1
        if line.find(cardplayer["name"]) != -1:
            data[counter - 1] = f"{cardplayer['name']} - {str(cardplayer['points'])}\n"

    with open('customers.txt', 'w') as file:
        file.writelines(data)


while True:  # Main game function
    if player["points"] <= 0:  # If the player has no points, save and exit the program
        print("Bard has wiped out your points. Thanks for playing. Better luck next time!")
        player_save(player)
        exit()

    if firstTime is True:  # If the game is just starting up, run through the first time setup
        first_time_setup()
        firstTime = False

    if player["hand"] == "":  # If player's hand is empty, allow them to bet.
        player["bet"] = bet(player)
        print(f"Betting {player['bet']} points.")
        time.sleep(1)

    if len(deck) < 5:  # Check if the deck is running low on cards, if so, repopulate the deck
        deck += repopulate_deck()
        print("Adding a new deck...")

    if player["hand"] == "":  # If cards were not dealt this round yet, deal them.
        dealer["hand"], dealer["card_value"] = deal(dealer)
        player["hand"], player["card_value"] = deal(player)
        dealer["hand"], dealer["card_value"] = deal(dealer)
        player["hand"], player["card_value"] = deal(player)

    if play is True:  # If the player is still allowed to play, don't show the dealer's second card
        print(f"\n\nDealer has: {dealer['hand'][:3]}?")
    else:
        print(f"\n\nDealer has: {dealer['hand']}, totaling {dealer['card_value']}")
    print(f"{player['name']} has: {player['hand']}, totaling {player['card_value']}")

    # Check to see if the player / dealer has blackjack, busted, or tied.
    playerValue = val_check(player)
    dealerValue = val_check(dealer)

    if dealerValue == "blackjack" and playerValue != "blackjack":  # Check if the dealer has blackjack
                                                                    # AND player doesn't
        print(colorama.Fore.RED + "Dealer has blackjack!" + colorama.Fore.RESET)
        time.sleep(1)
        calculate_winnings('dealer', 'bust')
        play = True
        continue

    if playerValue == "blackjack":  # Check if the Player has blackjack
        print(colorama.Fore.MAGENTA + f"{player['name']} has Blackjack!" + colorama.Fore.RESET)
        time.sleep(1)
        calculate_winnings('player', 'bj')
        play = True
        continue

    if dealerValue == 'bust':  # If dealer busted, player wins
        print(colorama.Fore.RED + f"Dealer busts on {dealer['card_value']}!" + colorama.Fore.RESET)
        calculate_winnings('player', 'win')
        play = True
        continue

    if player["choice"] == 's':  # If player stands, check dealer's cards
        if dealer["card_value"] < 17:  # If dealer card value isn't over 17, dealer draws.
            dealer["hand"], dealer["card_value"] = dealer_play(dealer)
        else:  # Otherwise, check to see who wins.
            if player["card_value"] > dealer["card_value"]:  # If player's cards are greater than dealer's
                calculate_winnings('player', 'win')
                play = True
            elif player["card_value"] < dealer["card_value"]:  # If dealer's cards are greater than player's
                if dealer["card_value"] <= 21:  # And dealer is under or equal to 21
                    calculate_winnings('dealer', 'win')
                else:  # Otherwise, dealer busted and player wins.
                    calculate_winnings('player', 'win')
                play = True
            else:  # If player and dealer tie
                calculate_winnings('player', 'tie')
                play = True
    else:  # Otherwise, player gets to play as long as they haven't busted.
        if playerValue != 'bust':
            if play is True and playerValue != "blackjack":  # If player doesn't have blackjack and can play, let them
                player["hand"], player["card_value"], player["choice"] = player_play(player)
                if player["choice"] == 's':  # If player chooses to stand in previous line, set play to false
                    play = False
        else:  # If player busted, dealer wins
            print(colorama.Fore.LIGHTRED_EX + f"{player['name']} has busted." + colorama.Fore.RESET)
            time.sleep(1)
            calculate_winnings('dealer', 'bust')
            play = True

    time.sleep(2)
