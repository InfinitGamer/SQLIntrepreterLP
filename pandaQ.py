import streamlit as st
import pandas as pd

from antlr4 import *
from pandaQLexer import pandaQLexer
from pandaQParser import pandaQParser
from pandaQVisitor import pandaQVisitor
import operator as op


class evalVisitor(pandaQVisitor):
    def __init__(self):

        # because SQL during order by can access the original table and the
        # table of select. We will have the same thing but in a unique table.
        self.tableForOrder = None
        self.currentState = None
        self.mapOrder = {'asc': True, 'desc': False}
        self.mapBoolean = {
            '=': op.eq,
            '!=': op.ne,
            '<': op.lt,
            '<=': op.le,
            '>': op.gt,
            '>=': op.ge,
            'not': op.neg,
            'and': op.and_,
            'or': op.or_
        }
        self.mapArithmetic = {
            '+': op.add,
            '-': op.sub,
            '*': op.mul,
            '/': op.truediv
        }

    def visitConsult(self, ctx: pandaQParser.ConsultContext):
        df = self.visit(ctx.consulta())
        st.table(df)

    def visitAssign(self, ctx: pandaQParser.AssignContext):
        df = self.visit(ctx.consulta())
        name = ctx.NAME().getText()
        st.session_state[name] = df.copy()
        st.table(df)

    def visitPlot(self, ctx: pandaQParser.PlotContext):
        name = ctx.NAME().getText()
        st.line_chart(st.session_state[name].select_dtypes('number'))

    def visitConsulta(self, ctx: pandaQParser.ConsultaContext):
        self.visit(ctx.selection())
        return self.currentState

    def visitSelection(self, ctx: pandaQParser.SelectionContext):
        self.visit(ctx.tables())
        if (ctx.where()):
            self.visit(ctx.where())

        self.visit(ctx.campos())

        if (ctx.order()):
            self.visit(ctx.order())

    def visitOrder(self, ctx: pandaQParser.OrderContext):
        nodes = ctx.preferencia()
        names = []
        ascending = []
        for i in nodes:
            name, prefe = self.visit(i)
            names.append(name)
            ascending.append(prefe)
        self.tableForOrder = self.tableForOrder.sort_values(
            by=names, ascending=ascending)
        self.currentState = self.currentState.reindex(self.tableForOrder.index)

    def visitPreferencia(self, ctx: pandaQParser.PreferenciaContext):
        name = ctx.NAME().getText()
        order = True
        if ctx.op:
            label = ctx.op.text
            order = self.mapOrder[label]
        return name, order

    def visitWhere(self, ctx: pandaQParser.WhereContext):
        cond = self.visit(ctx.condition())

        self.currentState = self.currentState.loc[cond]
        self.tableForOrder = self.currentState.copy()

    def visitNot(self, ctx: pandaQParser.NotContext):
        return ~self.visit(ctx.condition())

    def visitIsin(self, ctx: pandaQParser.IsinContext):
        columna = self.visit(ctx.campo2())
        df = evalVisitor().visit(ctx.consulta())
        l = columna.isin(df.values.flatten())
        return l

    def visitParetesis2(self, ctx: pandaQParser.Paretesis2Context):
        return self.visit(ctx.condition())

    def visitColumna(self, ctx: pandaQParser.ColumnaContext):
        return self.visit(ctx.campo2())

    def visitBooleanCondition(
            self,
            ctx: pandaQParser.BooleanConditionContext):
        cond1 = self.visit(ctx.condition(0))
        cond2 = self.visit(ctx.condition(1))
        op = ctx.op.text
        cond = self.mapBoolean[op](cond1, cond2)
        return cond

    def visitString(self, ctx: pandaQParser.StringContext):
        return ctx.NAME().getText()

    def visitTable(self, ctx: pandaQParser.TableContext):
        tabla = ctx.NAME().getText()
        try:

            path = tabla + ".csv"
            df = pd.read_csv(path)
            return df
        except FileNotFoundError as e:
            df = st.session_state[tabla]
            return df

    def visitTables(self, ctx: pandaQParser.TablesContext):
        df = self.visit(ctx.table())

        self.currentState = df
        self.tableForOrder = df.copy()
        if (ctx.inner()):
            self.visit(ctx.inner())

    def visitInner(self, ctx: pandaQParser.InnerContext):
        second_table = self.visit(ctx.table())
        name1 = ctx.NAME(0).getText()
        name2 = ctx.NAME(1).getText()
        self.currentState = self.currentState.merge(
            second_table, left_on=name1, right_on=name2, how='inner')
        self.tableForOrder = self.currentState.copy()
        if (ctx.inner()):
            self.visit(ctx.inner())

    def visitCampos(self, ctx: pandaQParser.CamposContext):
        nodes = ctx.campo()
        lista = []
        for i in nodes:
            lista.append(self.visit(i))
        ct = self.currentState
        ct = pd.concat(lista, axis=1)
        too = self.tableForOrder
        # we create a table for ordering that is the combination of
        # the original table (with columns that are might get
        # altered during selection)
        # and the new created ones
        # this part of code does this thing, update the existing ones and
        # concadente the new ones.
        common_columns = ct.columns.intersection(
            too.columns)
        too[common_columns] = ct[common_columns]
        too = pd.concat([ct,
                         too.loc[:,
                                 ~too.columns.isin(ct.columns)]],
                        axis=1)
        self.currentState = ct
        self.tableForOrder = too

    def visitCampo(self, ctx: pandaQParser.CampoContext):
        columna = self.visit(ctx.campo2())
        if (ctx.AS()):
            new_col = ctx.NAME().getText()
            columna = columna.rename(new_col)
        return columna

    def visitMinus(self, ctx: pandaQParser.MinusContext):
        valor = self.visit(ctx.campo2())
        return -1 * valor

    def visitArithmetic(self, ctx: pandaQParser.ArithmeticContext):
        [node0, _, node1] = list(ctx.getChildren())
        node0 = self.visit(node0)
        node1 = self.visit(node1)
        op = ctx.op.text
        return self.mapArithmetic[op](node0, node1)

    def visitParetesis(self, ctx: pandaQParser.ParetesisContext):
        return self.visit(ctx.campo2())

    def visitNumero(self, ctx: pandaQParser.NumeroContext):
        return self.visit(ctx.num())

    def visitNum(self, ctx: pandaQParser.NumContext):
        num = ctx.NUM().getText()
        num = float(num)

        if (ctx.MINUS()):
            num *= -1.0
        return num

    def visitColumn(self, ctx: pandaQParser.ColumnContext):
        nombre = ctx.nombre.text
        if nombre != "*":
            return self.currentState[nombre]
        return self.currentState


title = st.text_input("Query:")

button = st.button("Submit")

if button:
    input_stream = InputStream(title)
    lexer = pandaQLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = pandaQParser(token_stream)

    tree = parser.root()
    # print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
    # print(tree.toStringTree(recog=parser))
    if parser.getNumberOfSyntaxErrors() == 0:
        visitor = evalVisitor()
        df = visitor.visit(tree)
