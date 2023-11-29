grammar sqlinterpreter;
root : consulta SEMICOLON      // l'etiqueta ja és root
     ;

consulta: selection ;
selection: SELECT campos tables (order)?;
order: ORDER BY preferencia ( COMA preferencia)*;
preferencia : NAME op=(ASC | DES)?;
tables: FROM NAME;
campos: campo (COMA campo)*;
campo : campo2 (AS NAME)?;

campo2: PAROP campo2 PARCL #paretesis
      | campo2 (MUL | DIV) num #mulDiv
      | num (MUL | DIV) campo2 #mulDiv
      | campo2 (MUL | DIV) campo2 #mulDiv
      | campo2 (SUMA | MINUS) num #sumMinus
      | num (SUMA | MINUS) campo2 #sumMinus
      | campo2 (SUMA | MINUS) campo2 #sumMinus
      | nombre=(NAME|MUL) #column
;

num: NUM;

SUMA: '+';
MINUS: '-'; 
MUL: '*';
DIV: '/';
PAROP: '(';
PARCL: ')';
SELECT : 'select';
FROM : 'from';
SEMICOLON :';';
ORDER: 'order';
BY : 'by';
ASC: 'asc';
DES: 'desc';
COMA: ',';
AS: 'as';
NAME : (CHARACTER (CHARACTER|[0-9])*);

NUM: [0-9]+ ('.'[0-9]+)?;
CHARACTER : [a-zA-Z] | '_';

WS : [ \t\n\r]+ -> skip ;

