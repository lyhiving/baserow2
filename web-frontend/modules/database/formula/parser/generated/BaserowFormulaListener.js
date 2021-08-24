// Generated from BaserowFormula.g4 by ANTLR 4.8
// jshint ignore: start
var antlr4 = require('antlr4/index');

// This class defines a complete listener for a parse tree produced by BaserowFormula.
function BaserowFormulaListener() {
	antlr4.tree.ParseTreeListener.call(this);
	return this;
}

BaserowFormulaListener.prototype = Object.create(antlr4.tree.ParseTreeListener.prototype);
BaserowFormulaListener.prototype.constructor = BaserowFormulaListener;

// Enter a parse tree produced by BaserowFormula#root.
BaserowFormulaListener.prototype.enterRoot = function(ctx) {
};

// Exit a parse tree produced by BaserowFormula#root.
BaserowFormulaListener.prototype.exitRoot = function(ctx) {
};


// Enter a parse tree produced by BaserowFormula#StringLiteral.
BaserowFormulaListener.prototype.enterStringLiteral = function(ctx) {
};

// Exit a parse tree produced by BaserowFormula#StringLiteral.
BaserowFormulaListener.prototype.exitStringLiteral = function(ctx) {
};


// Enter a parse tree produced by BaserowFormula#FunctionCall.
BaserowFormulaListener.prototype.enterFunctionCall = function(ctx) {
};

// Exit a parse tree produced by BaserowFormula#FunctionCall.
BaserowFormulaListener.prototype.exitFunctionCall = function(ctx) {
};


// Enter a parse tree produced by BaserowFormula#func_name.
BaserowFormulaListener.prototype.enterFunc_name = function(ctx) {
};

// Exit a parse tree produced by BaserowFormula#func_name.
BaserowFormulaListener.prototype.exitFunc_name = function(ctx) {
};


// Enter a parse tree produced by BaserowFormula#identifier.
BaserowFormulaListener.prototype.enterIdentifier = function(ctx) {
};

// Exit a parse tree produced by BaserowFormula#identifier.
BaserowFormulaListener.prototype.exitIdentifier = function(ctx) {
};



exports.BaserowFormulaListener = BaserowFormulaListener;