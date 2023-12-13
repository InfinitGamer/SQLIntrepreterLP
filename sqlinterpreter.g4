grammar sqlinterpreter;
root : consulta SEMICOLON      // l'etiqueta ja és root
     ;

consulta: selection ;
selection: SELECT campos tables (where)? (order)?;
order: ORDER BY preferencia ( COMA preferencia)*;
preferencia : NAME op=(ASC | DES)?;
tables: FROM table (inner)?;
table: NAME;
inner: INNER JOIN table ON NAME EQ NAME (inner)?;
campos: campo (COMA campo)*;
campo : campo2 (AS NAME)?;
where: WHERE condition;

condition: PAROP condition PARCL #paretesis2
         | condition op=(LT|LE|GT|GE|EQ|NEQ) condition #booleanCondition
         | NOT condition #not
         | condition op=AND condition #booleanCondition
         | condition op=OR condition #booleanCondition
         | COMILLAS NAME COMILLAS #string
         | campo2 #columna
         ;

campo2: MINUS campo2 #minus 
      | PAROP campo2 PARCL #paretesis
      | campo2 (MUL | DIV) campo2 #mulDiv
      | campo2 (SUMA | MINUS) campo2 #sumMinus
      | num #numero
      | nombre=(NAME|MUL) #column
;

num:op=(SUMA|MINUS)? NUM;

LT: '<';
LE: '<=';
GT: '>';
GE: '>=';
EQ:'=';
NEQ:'!=';
NOT: 'not';
AND: 'and';
OR:'or';
INNER: 'inner';
JOIN: 'join';
ON:'on';
SUMA: '+';
MINUS: '-'; 
MUL: '*';
DIV: '/';
PAROP: '(';
PARCL: ')';
SELECT : 'select';
FROM : 'from';
SEMICOLON :';';
WHERE: 'where';
ORDER: 'order';
BY : 'by';
ASC: 'asc';
DES: 'desc';
COMA: ',';
AS: 'as';
COMILLAS: '"';
NAME : (CHARACTER (CHARACTER|[0-9])*);

NUM: [0-9]+ ('.'[0-9]+)?;
CHARACTER : [a-zA-Z] | '_';

WS : [ \t\n\r]+ -> skip ;

