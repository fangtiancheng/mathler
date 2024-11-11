# Mathler Game

**Mathler** is a math-based puzzle game inspired by Wordle, where players attempt to guess a mathematical expression that evaluates to a target result within a limited number of guesses. This repository provides the first open-source (maybe, at least I haven't found an earlier implementation) Python implementation of the game on github, complete with features such as expression validation, guess feedback, and visual representations of game progress.

## Features

- **Expression Generation**: Dynamically generates random mathematical expressions of customizable length that evaluate to integer values within a specified range.
- **Expression Validation**: Ensures guesses contain only valid operators and integers, and evaluates if the guessed expression equals the target value.
- **Guess Feedback**: Provides visual feedback for each guess, indicating correct digits/characters in correct positions, partially correct characters, and incorrect characters.
- **Hint System**: Offers hints by displaying which characters are correct or partially correct in a guessed expression.
- **Customizable Visual Output**: Uses the PIL library to create images that visually display the game board and feedback for each guess.

## Requirements

- Python 3.8+
- Required libraries:
  - `Pillow` for image generation and visual feedback.

Install the necessary packages using:

```bash
pip install pillow
```

## Game Setup

The `MathlerGame` class initializes the game with a target expression. Players can use the following methods to interact with the game:

### `__init__(self, word: str)`

Creates a new game instance with the target mathematical expression. For instance:

```python
mathler = MathlerGame('1+2+3+4')
```

### `guess(self, word: str) -> Tuple[GuessResult, str]`

Allows the player to submit a guess. The function returns feedback indicating the result:
- `WIN`: The guess matches the target expression.
- `LOSS`: The player has used all allowed attempts without finding the target.
- `DUPLICATE`: The guess is a repeat of a previous attempt.
- `ILLEGAL`: The guess contains invalid characters or operators.
- `LEGAL`: The guess is valid but incorrect.

Example:

```python
result, message = mathler.guess('1+3+3+3')
print(result, message)
```

### `draw(self, savePath: str)`

Generates a visual representation of the game board, showing each guess and feedback on correctness. The image is saved to the specified path.

Example:

```python
mathler.draw('/path/to/save/game_board.png')
```

### `get_hint(self) -> str`

Generates a string with hints for the player by revealing letters or symbols that are correct or partially correct in the guesses made so far.

Example:

```python
hint = mathler.get_hint()
print("Hint:", hint)
```

### `draw_hint(self, hint: str, savePath: str)`

Creates an image displaying the hint provided by `get_hint()` and saves it to the specified path.

Example:

```python
mathler.draw_hint(hint, '/path/to/save/hint.png')
```

## Customization

Several properties of the game visuals, such as block size, padding, colors, and font, can be adjusted directly in the `MathlerGame` class to suit your preferences.

## Example

Here is a complete example of creating a Mathler game, making guesses, and generating visuals:

```python
from MathlerGame import MathlerGame

mathler = MathlerGame('1+2+3+4')

# Guess attempts
print(mathler.guess('6//3+21'))
mathler.draw('game_board_1.png')

print(mathler.guess('1+3+3+3'))
mathler.draw('game_board_2.png')

print(mathler.guess('1+2+3+4'))
mathler.draw('game_board_3.png')

# Hint generation
hint = mathler.get_hint()
mathler.draw_hint(hint, 'hint_image.png')
```

## Contribution

Feel free to fork this repository, submit pull requests, or report any issues. Contributions are welcome!

## License

This project is licensed under the MIT License.

## Example

![](./data/sample/game.jpg)