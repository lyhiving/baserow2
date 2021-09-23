# Understanding Baserow Formulas

Baserow supports user created formula fields which given a formula from the user
calculate the result of that formula for every row. Baserow formulas look and work very
similarly to formulas found in other spreadsheet tools, so if you have formula already
you will find working with them in Baserow very natural.

This guide will first explain what Baserow formulas are and how to use them. 

See the [baserow formula technical guide](./formula-technical-guide.md) if you are a
developer looking for a technical understanding of how formulas are implemented 
within Baserow.

## What a Baserow Formula Field is

A Baserow Formula field lets you create a field whose contents are calculated based on a
Baserow Formula you've provided. A Baserow Formula is simply some text written in a
particular way such that Baserow can understand it, for example the text `1+1` is a
Baserow formula and when set on a formula field every cell in that field will contain
the result `2`.

### A Simple Formula Example

For example imagine you have a table with a normal text field called `text field` with
rows of `one`,`two` and `three` . You could then add a formula field with a formula
of `concat('Number', field('text field'))` and the results would look like:

| text field | formula field |
|------------|---------------|
| one        | Number one    |
| two        | Number two    |
| three      | Number three  |

As you can see the contents of the formula field are calculated based on the value of
the text field per row. Don't worry if it's not clear how the formula above worked, 
we'll break it down in the next few sections bit by bit.

### Formulas can reference other fields

As you might have noticed above in the simple example in the formula we wrote `field
('text field')`. This tells Baserow to go and fetch the value of the field with that 
name and use it in the formula for that row. So if we clicked on the 
formula field's dropdown arrow and selected `Edit field` and changed the formula to just
be `field('text field')` and saved our change by clicking the blue `Change` button 
the resulting table would look like:

| text field | formula field |
|------------|---------------|
| one        | one           |
| two        | two           |
| three      | three         |

As you can see our formula field now just contains whatever is in the text field for 
each row. By referencing other fields you can construct powerful formulas which will 
save you having to manually do things! 

> What would happen if we changed the formula to `field('unknown field')`? 
> 
> Answer: The Baserow formula field is marked with an error and all of it's cells go 
> blank as there is no way to calculate a result as there is no 
> field called `unknown field` in this table. You can only reference fields in the 
> same table inside of a formula.

### Using Functions

Remember from the first example where we wrote `concat(` some stuff `)`? Inside of a 
formula this is an example of using a function. A function is simply a way of 
telling Baserow to calculate a result based on some input. The `concat`
function can be given as many inputs as you want and it will concatenate 
(think join together) them all and output them as one big long piece of text. For 
example the formula `concat('a', 'b', 'c')` results in `'abc'`. 

To use a function in a formula you first write the name of the function, in our case
`concat`. Then you need to put an opening bracket `(` to tell Baserow you are starting
the list of inputs. Next after the opening bracket you can write any valid 
Baserow formula as an input. You can pass multiple formulas to a function which can 
handle multiple inputs by separating them with `,`s. Finally, once you have finished 
specifying the inputs to the function you need tell Baserow by typing a closing 
bracket `)`.

### Writing text directly in formulas

In the example above we wrote `concat('a', 'b', 'c')` to get `'abc'`. But what does 
these single quotes around the `a` , `b` and `c` characters mean? And why when I write 
instead `concat(a,b,c)` do I get an error? 

This is all because when you want to use text directly in a formula you need to tell 
Baserow what you are typing in should be treated as literally that piece of text, 
which you do by surrounding it with single `'` or double `"` quotes. 

If you rename a field referenced in another formula 
field's formula then it will also rename inside of that formula.

If you were to then change one of the text field cells you would see the change
instantly happen for the corresponding formula field.


### Formula Field Cells cannot be edited directly

One key thing to understand is that you can't now go in and change the value of say the
formula field cell containing the value `Number two` to `Number two!`. This is because
the contents of the cell are always fixed t

