import argparse, traceback
from decimal import Decimal

from modeling.data import *


def DCF(ticker, ev_statement, income_statement, balance_statement, cashflow_statement, discount_rate, forecast, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate):
    enterprise_val = enterprise_value(income_statement,
                                        cashflow_statement,
                                        balance_statement,
                                        forecast, 
                                        discount_rate,
                                        earnings_growth_rate, 
                                        cap_ex_growth_rate, 
                                        perpetual_growth_rate)

    equity_val, share_price = equity_value(enterprise_val,
                                           ev_statement)

    print('\nEnterprise Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(enterprise_val))), 
              '\nEquity Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(equity_val))),
           '\nPer share value for {}: ${}.\n'.format(ticker, '%.2E' % Decimal(str(share_price))),
            )

    return {
        'date': income_statement[0]['date'],       # statement date used
        'enterprise_value': enterprise_val,
        'equity_value': equity_val,
        'share_price': share_price
    }


def historical_DCF(ticker, years, forecast, discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, interval = 'annual', apikey = ''):
    dcfs = {}

    income_statement = get_income_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    balance_statement = get_balance_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    cashflow_statement = get_cashflow_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    enterprise_value_statement = get_EV_statement(ticker = ticker, period = interval, apikey = apikey)['enterpriseValues']

    if interval == 'quarter':
        intervals = years * 4
    else:
        intervals = years

    for interval in range(0, intervals):
        try:
            dcf = DCF(ticker, 
                    enterprise_value_statement[interval],
                    income_statement[interval:interval+2],        
                    balance_statement[interval:interval+2],
                    cashflow_statement[interval:interval+2],
                    discount_rate,
                    forecast, 
                    earnings_growth_rate,  
                    cap_ex_growth_rate, 
                    perpetual_growth_rate)
        except (Exception, IndexError) as e:
            print(traceback.format_exc())
            print('Interval {} unavailable, no historical statement.'.format(interval)) # catch
        else: dcfs[dcf['date']] = dcf 
        print('-'*60)
    
    return dcfs


def ulFCF(ebit, tax_rate, non_cash_charges, cwc, cap_ex):
    return ebit * (1-tax_rate) + non_cash_charges + cwc + cap_ex


def get_discount_rate():
    return .1 # TODO: implement 


def equity_value(enterprise_value, enterprise_value_statement):
    equity_val = enterprise_value - enterprise_value_statement['+ Total Debt'] 
    equity_val += enterprise_value_statement['- Cash & Cash Equivalents']
    share_price = equity_val/float(enterprise_value_statement['Number of Shares'])

    return equity_val,  share_price


def enterprise_value(income_statement, cashflow_statement, balance_statement, period, discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate):
    if income_statement[0]['EBIT']:
        ebit = float(income_statement[0]['EBIT'])
    else:
        ebit = float(input(f"EBIT missing. Enter EBIT on {income_statement[0]['date']} or skip: "))
    tax_rate = float(income_statement[0]['Income Tax Expense']) /  \
               float(income_statement[0]['Earnings before Tax'])
    non_cash_charges = float(cashflow_statement[0]['Depreciation & Amortization'])
    cwc = (float(balance_statement[0]['Total assets']) - float(balance_statement[0]['Total non-current assets'])) - \
          (float(balance_statement[1]['Total assets']) - float(balance_statement[1]['Total non-current assets']))
    cap_ex = float(cashflow_statement[0]['Capital Expenditure'])
    discount = discount_rate

    flows = []

    # Now let's iterate through years to calculate FCF, starting with most recent year
    print('Forecasting flows for {} years out, starting at {}.'.format(period, income_statement[0]['date']),
         ('\n         DFCF   |    EBIT   |    D&A    |    CWC     |   CAP_EX   | '))
    for yr in range(1, period+1):    

        # increment each value by growth rate
        ebit = ebit * (1 + (yr * earnings_growth_rate))
        non_cash_charges = non_cash_charges * (1 + (yr * earnings_growth_rate))
        cwc = cwc * 0.7                             # TODO: evaluate this cwc rate? 0.1 annually?
        cap_ex = cap_ex * (1 + (yr * cap_ex_growth_rate))         

        # discount by WACC
        flow = ulFCF(ebit, tax_rate, non_cash_charges, cwc, cap_ex)
        PV_flow = flow/((1 + discount)**yr)
        flows.append(PV_flow)

        print(str(int(income_statement[0]['date'][0:4]) + yr) + '  ',
              '%.2E' % Decimal(PV_flow) + ' | ',
              '%.2E' % Decimal(ebit) + ' | ',
              '%.2E' % Decimal(non_cash_charges) + ' | ',
              '%.2E' % Decimal(cwc) + ' | ',
              '%.2E' % Decimal(cap_ex) + ' | ')

    NPV_FCF = sum(flows)
    
    # calculating terminal value using perpetual growth rate
    final_cashflow = flows[-1] * (1 + perpetual_growth_rate)
    TV = final_cashflow/(discount - perpetual_growth_rate)
    NPV_TV = TV/(1+discount)**(1+period)

    return NPV_TV+NPV_FCF

