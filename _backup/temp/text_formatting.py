class TextParams():

    def __init__(self):
        
        self.items = ['Total revenue', 'Cost of goods sold', 'Deprecation and amortization',
                'Depreciation', 'Amortization of intangibles',
                'Amortization of deferred charges', 'Other cost of goods sold',
                'Gross profit', 'Operating expenses (excl. COGS)',
                'Selling/general/admin expenses, total', 'Research & development',
                'Selling/general/admin expenses, other',
                'Other operating expenses, total', 'Operating income',
                'Non-operating income, total',
                'Interest expense, net of interest capitalized',
                'Interest expense on debt', 'Interest capitalized',
                'Non-operating income, excl. interest expenses',
                'Non-operating interest income', 'Pretax equity in earnings',
                'Miscellaneous non-operating expense', 'Unusual income/expense',
                'Impairments', 'Restructuring charge', 'Legal claim expense',
                'Unrealized gain/loss', 'Other exceptional charges', 'Pretax income',
                'Equity in earnings', 'Taxes', 'Income tax, current',
                'Income tax, current - domestic', 'Income Tax, current - foreign',
                'Income tax, deferred', 'Income tax, deferred - domestic',
                'Income tax, deferred - foreign', 'Income Tax Credits',
                'Non-controlling/minority interest', 'After tax other income/expense',
                'Net income before discontinued operations', 'Discontinued operations',
                'Net income', 'Dilution adjustment', 'Preferred dividends',
                'Diluted net income available to common stockholders',
                'Basic earnings per share (Basic EPS)',
                'Diluted earnings per share (Diluted EPS)',
                'Average basic shares outstanding', 'Diluted shares outstanding',
                'EBITDA', 'EBIT', 'Total operating expenses']

        self.item_keys = []

        for item in self.items:
            item_temp = item
            item_temp = item_temp.lower()
            item_temp = item_temp.replace(' - ', '_')
            item_temp = item_temp.replace('-', '_')
            item_temp = item_temp.replace(' ', '_')
            item_temp = item_temp.replace('(', '')
            item_temp = item_temp.replace(')', '')
            item_temp = item_temp.replace('&', 'and')
            item_temp = item_temp.replace('.', '')
            item_temp = item_temp.replace(',', '')
            item_temp = item_temp.replace('/', '_')
            # print(f"self.{item_temp}_str = '{item}'")
            self.item_keys.append(item_temp)


        # self.res = {}
        # for key in self.item_keys:
        #     for value in self.items:
        #         self.res[key] = value
        #         self.items.remove(value)
        #         break


        # print(self.res)


test = TextParams()