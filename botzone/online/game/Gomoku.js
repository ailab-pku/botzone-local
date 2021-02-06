//
//  Leedy
//  2014-10-7
//

var SIZE = 15;    // 棋盘大小 15*15
var Grid = new Array(SIZE);
for (var i = Grid.length - 1; i >= 0; i--) {
  Grid[i] = new Array(SIZE);
}
var inGrid = function(x, y) {
  return x >= 0 && x < SIZE && y >= 0 && y < SIZE;
};
var gridFull = function() {
  for (var i = 0; i < SIZE; i++) {
    for (var j = 0; j < SIZE; j++) {
      if (Grid[i][j] === undefined) {
        return false;
      }
    }
  }
  return true;
};
var placeAt = function(color, x, y) {
  if (inGrid(x, y) && Grid[x][y] === undefined) {
    Grid[x][y] = color;
    return true;
  } else {
    return false;
  }
};
var winAfterPlaceAt = function(color, x, y) {
  var checkTowards = function(xx, yy) {
    var x_, y_;
    for (var i = 0; i < 5; i++) {
      x_ = x + xx*i;
      y_ = y + yy*i;
      if (!inGrid(x_, y_) || Grid[x_][y_] !== color) {
        break;
      }
    }
    for (var j = 0; j < 5; j++) {
      x_ = x - xx*j;
      y_ = y - yy*j;
      if (!inGrid(x_, y_) || Grid[x_][y_] !== color) {
        break;
      }
    }
    return i + j - 1;
  };
  return checkTowards(1, 0) >= 5 || checkTowards(0, 1) >= 5 || checkTowards(1, 1) >= 5 || checkTowards(1, -1) >= 5;
};

process.stdin.resume();
process.stdin.setEncoding('utf8');

var fullInput = "";
process.stdin.on('data', function(chunk) {
  fullInput += chunk;
});

process.stdin.on('end', function() {
  var input = JSON.parse(fullInput).log;  // Array
  var output; // undefined
  if (input.length === 0) {
    output = {
      command: "request",
      content: {
        0: {x: -1, y: -1}
      }
    };
  } else {
    for (var i = 1; i < input.length; i += 2) { // length = 2, 4, 6, 8 ...
      var color = (i-1) / 2 % 2;  // 1 => 0, 3 => 1, 5 => 0 ..., 0: black, 1: white
      var response = input[i][color].response || input[i][color].content || {};
      var isLast = (i === (input.length - 1));
      if (parseInt(response.x) !== response.x || parseInt(response.y) !== response.y) {
        output = {
          display: {
            winner: +!color,
            error: "INVALID INPUT",
            error_data: response
          },
          command: "finish",
          content: {
            0: color * 2,
            1: !color * 2
          }
        };
        break;
      }
      if (placeAt(color, response.x, response.y)) {
        if (isLast) {
          output = {
            display: {    // 用于实时对战
              color: color,
              x: response.x,
              y: response.y
            }
          };
          if (winAfterPlaceAt(color, response.x, response.y)) {
            output.command = "finish";
            output.display.winner = color;
            output.content = {
              0: !color * 2,
              1: color * 2
            };
          } else if (gridFull()) {
            output.command = "finish";
            output.content = { 0: 1, 1: 1 };
          } else {
            output.command = "request";
            output.content = {};
            output.content[+!color] = {
              x: response.x,
              y: response.y
            };
          }
        }
      } else { // invalid input
        output = {
          display: {
            winner: +!color,
            error: "INVALID MOVE",
            error_data: response
          },
          command: "finish",
          content: {
            0: color * 2,
            1: !color * 2
          }
        };
        break;
      }
    }
  }
  console.log(JSON.stringify(output));
});

/********************************** TEST **********************************

console.log(inGrid(1, 1) === true);
console.log(inGrid(-1, 1) === false);
placeAt(0, 0, 1);
placeAt(0, 0, 3);
placeAt(0, 0, 4);
placeAt(0, 0, 5);
console.log(winAfterPlaceAt(0, 0, 5) === false);
placeAt(0, 0, 2);
console.log(winAfterPlaceAt(0, 0, 2) === true);

************************************ END **********************************/
