__author__ = 'Alex'


#Source: http://codingwithnumbers.blogspot.com/2012/03/create-mortgage-amortization-table-in.html

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   Title:  finance_calc.py
#   Author: Manasseh, Alexander
#   Maj.Ver:    0
#   Min.Ver:    1
#   Rev.    0
#   Rel Date:
#   Date Modified:
#
#   Changelog:
#   3/14/2015: overhaulled the evaluate method in the financing class produces proper dates.  Also included demo code
#   2/28/2015: Adding general transaction class, portfolio class, investment class
#   2/27/2015: Functioning loan object with additional payments function, object for flat expenses
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#TODO:  Read loan info from xml file or config file
#TODO:  Re-architect code to allow dynamic generation of payments that are not bound by an end date
#TODO:  Complete the milestone code (actual date, actual balance)
#TODO:  Write a function to print out a table of all transactions and balances after the milestone, but prior to request date
#TODO:  Create snowball method for Portfolio (Flag sum of money to be disbursed, prioritized)

from decimal import *
import datetime

def nextDate(startDate, period, interval):
    '''Returns the date from the startDate, given a period type (monthly, annually, weekly or daily) and interval
    (number of periods)
    '''
    import string
    import datetime


    if period == "m" or period == "M" or period.lower() == "month" or period.lower() == "monthly":
        deltaYear = (startDate.month + interval-1)/12
        newMonth = (startDate.month + interval -1) % 12 + 1
        newDate = (datetime.datetime( Decimal(startDate.year + deltaYear), newMonth, startDate.day))
    elif period == "a" or period == "A" or period.lower() == "annual" or period.lower() == "annually":
        newDate = (datetime.datetime(startDate.year+interval, startDate.month, startDate.day))
    elif period == "w" or period == "W" or period.lower() == "week" or period.lower() == "weekly":
        newDate = (startDate + datetime.timedelta(weeks=interval))
    elif period == "d" or period == "D" or period.lower() == "day" or period.lower() == "daily":
        newDate = (startDate + datetime.timedelta(days=interval))
    else:
        raise ValueError("No Valid Period Entered.  Enter period as Monthly: \"m\" or \"M\", "
                         "Annually: \"a\" or \"A\", Weekly: \"w\" or \"W\", Daily:\"d\",\"D\"")

    return newDate


def numPeriods(startDate, period):
    #find the number of pay periods within a year
    import string
    if period == "m" or period == "M" or period.lower() == "month" or period.lower() == "monthly":
        numPeriod = 12
    elif period == "a" or period == "A" or period.lower() == "annual" or period.lower() == "annually":
        numPeriod = 1
    elif period == "w" or period == "W" or period.lower() == "week" or period.lower() == "weekly":
        numPeriod = 52
    elif period == "d" or period == "D" or period.lower() == "day" or period.lower() == "daily":
        import calendar
        if calendar.isleap(startDate.year):
            numPeriod = 366
        else:
            numPeriod = 365
    else:
        raise ValueError("No Valid Period Entered.  Enter period as Monthly: \"m\" or \"M\", "
                         "Annually: \"a\" or \"A\", Weekly: \"w\" or \"W\", Daily:\"d\",\"D\"")
    return numPeriod


def pmt(principal, rate, term, startDate, period):
    '''Calculates the payment on a loan.

    Returns the payment amount on a loan given
    the principal, the interest rate (as an APR),
    and the term (in months).'''
    import string
    if period == "m" or period == "M" or period.lower() == "month" or period.lower() == "monthly":
        ratePerTwelve = rate / (12 * 100.0)
    elif period == "a" or period == "A" or period.lower() == "annual" or period.lower() == "annually":
        ratePerTwelve = rate / (1 * 100.0)
    elif period == "w" or period == "W" or period.lower() == "week" or period.lower() == "weekly":
        ratePerTwelve = rate / (52 * 100.0)
    elif period == "d" or period == "D" or period.lower() == "day" or period.lower() == "daily":
        import calendar
        if calendar.isleap(startDate.year):
            ratePerTwelve = rate / (366 * 100.0)
        else:
            ratePerTwelve = rate / (365 * 100.0)
    else:
        raise ValueError("No Valid Period Entered.  Enter period as Monthly: \"m\" or \"M\", "
                         "Annually: \"a\" or \"A\", Weekly: \"w\" or \"W\", Daily:\"d\",\"D\"")


    result = principal * (ratePerTwelve / (1 - (1 + ratePerTwelve) ** (-term)))

    # Convert to decimal and round off to two decimal
    # places.
    result = Decimal(result)
    result = (result)
    return result


def dateParser(userDate):
    #TODO:  Troubleshoot issues where dateParser cannot accept datetime.datetime objects
    import datetime
    # if type(userDate) == type(datetime.datetime):
    #     return userDate
    # else:
    try:
        formattedStartDate = datetime.datetime.strptime(userDate, "%m/%d/%Y")
    except ValueError:
        print("ValueError for MM/DD/YYYY format, checking for DD/MM/YYYY format")
        try:
            formattedStartDate = datetime.datetime.strptime(userDate, "%d/%m/%Y")
        except ValueError:
            print("ValueError for DD/MM/YYYY format, checking for DD Mon YYYY format")
            formattedStartDate = datetime.datetime.strptime(userDate, "%d %b %Y")
    except TypeError:
        return userDate
    return formattedStartDate


class Portfolio:
    #TODO:  Add string lookup for a entry by the .name attribute of an entry (use name rather than index)
    #TODO:  Add function to return the financial object from the mortgage, etc. arrays given the name of the loan
    def __init__(self, name, startDate = None):
        self.name = name
        self.startDate = dateParser(startDate) # This date is the date at which expenses and credits will begin to be evaluated
        self.transactionArray = []
        self.mortgageArray = []
        self.loanArray = []
        self.investmentArray = []
        self.mileStone = []

        self.transact = []
        self.credits = []
        self.assets = []
        self.balance = []

        self.mortgageDef = {}
        self.loanDef = {}
        self.investmentDef = {}
        self.transactionDef = {}

    def addMilestone(self, date, balance):
        tempDate = dateParser(date)
        self.mileStone.append( (tempDate, balance ))
        self.evaluate()

    def addMortgage(self, principal, rate, term, startDate, period, interval, name=None):
        tempMortgage = loan(principal, rate, term, startDate, period, interval, name)
        self.mortgageArray.append(tempMortgage)
        self.mortgageDef[name] = len(self.mortgageArray) - 1
        self.evaluate()
        return len(self.mortgageArray)-1

    def addMortPayment(self, loanName, payment, startDate, term, period, interval):
        procStartDate = dateParser(startDate)
        # print self.mortgageDef.get(loanName, "")
        for index in range(0, term):
            self.mortgageArray[self.mortgageDef.get(loanName, "")].addPayment(nextDate(procStartDate,period, index*interval), payment)

        self.evaluate()

    def addLoanPayment(self, loanName, payment, startDate, term, period, interval):
        procStartDate = dateParser(startDate)
        # print procStartDate

        # print self.mortgageDef.get(loanName, "")
        for index in range(0, term):
            payDate = nextDate(procStartDate,period, index*interval)
            # print payDate
            self.loanArray[self.loanDef.get(loanName, "")].addPayment(payDate, payment)
            # print self.loanArray[self.loanDef.get(loanName, "")].name

        self.evaluate()

    def addLoan(self, principal, rate, term, startDate, period, interval, name=None):
        tempLoan = loan(principal, rate, term, startDate, period, interval, name)
        self.loanArray.append(tempLoan)
        self.loanDef[name] = len(self.loanArray) - 1
        self.evaluate()
        return len(self.loanArray)-1

    def addInvestment(self, principal, rate, term, startDate, endDate, period, interval, name=None):
        tempInvestment = investment(principal, rate, term, startDate, endDate, period, interval, name=None)
        self.investmentArray.append(tempInvestment)
        self.investmentDef[name] = len(self.investmentArray) - 1
        self.evaluate()
        return len(self.investmentArray)-1

    def addExpense(self, amount, startDate, endDate, period, interval, name=None, num_times=float('inf')):
        tempTransaction = regularPayment(-1*abs(amount), startDate, endDate, period, interval, name, num_times=float('inf'))
        self.transactionArray.append(tempTransaction)
        self.transactionDef[name] = len(self.transactionArray) - 1
        self.evaluate()
        return len(self.transactionArray)-1

    def addIncome(self, amount, startDate, endDate, period, interval, name=None, num_times=float('inf')):
        tempTransaction = regularIncome(abs(amount), startDate, endDate, period, interval, name, num_times=float('inf'))
        self.transactionArray.append(tempTransaction)
        self.transactionDef[name] = len(self.transactionArray) - 1
        self.evaluate()
        return len(self.transactionArray)-1

    def prioritizeLoans(self, scheme="snowball"):
        '''
        This function sorts all loans/mortgages according to whatever scheme is set
        '''
        from operator import itemgetter

        self.mortgageIndex = len(self.mortgageArray)

        # Create list of loans with appropriate sorting method
        self.rateList = []
        for index in range(0, len(self.mortgageArray)):
            self.rateList.append( (self.mortgageArray[index].rate, self.mortgageArray[index].startBalance[0], index) )
        for index in range(0, len(self.loanArray)):
            self.rateList.append( (self.loanArray[index].rate,self.loanArray[index].startBalance[0], index + len(self.mortgageArray)))

        #Return a list sorted by rate, then balance amt
        self.rateList = sorted(self.rateList, key=itemgetter(1), reverse=True)
        self.rateList = sorted(self.rateList, key=itemgetter(0), reverse=True)

    def evaluate(self):

        self.transact = []
        self.assets = []

        #concatenate all mortgages, loans, and investments
        for mortgage in self.mortgageArray:
            for index in range(0, len(mortgage.transDate)):
                self.transact.append( (mortgage.transDate[index], mortgage.name, mortgage.payment[index]) )
                self.assets.append( (mortgage.transDate[index], mortgage.name, mortgage.pPayment[index]) )
        for loan in self.loanArray:
            for index in range(0, len(loan.transDate)):
                self.transact.append( (loan.transDate[index], loan.name, loan.payment[index]) )
        for investment in self.investmentArray:
            for index in range(0, len(investment.transDate)):
                self.assets.append( (investment.transDate[index], investment.name, investment.balance[index]) )
        for transaction in self.transactionArray:
            for index in range(0, len(transaction.transDate)):
                self.transact.append( (transaction.transDate[index], transaction.name, transaction.payment[index]) )

        self.assets.sort()
        self.transact.sort()

        self.mileStone.sort()

        if self.mileStone:
            del_buffer = 0
            for index, transaction in enumerate(self.transact):
                if transaction[0] < self.mileStone[-1][0]:
                    del_buffer = index
            self.transactionAbridged = self.transact[del_buffer+1:]

            #self.balance = [(entry[0], entry[1], self.mileStone[-1][1] + entry[2]) for entry in self.tempTransact ]
            self.balance.append((self.mileStone[-1][0], "Starting Balance", self.mileStone[-1][1], 0))
            for index, entry in enumerate(self.transactionAbridged):
                self.balance.append( (entry[0], entry[1], Decimal(entry[2]) + Decimal(self.balance[-1][2]), entry[2]))

    def debtSnowball(self, amount, startDate, endDate, period, interval):


        self.prioritizeLoans()
        for loan in self.rateList:
            print (loan)
            if loan[2] < len(self.mortgageArray):

                num=1
                payDate = 0
                while self.mortgageArray[loan[2]].startBalance[-1] !=0 and payDate < dateParser(endDate):
                    payDate = nextDate(startDate, period, interval*num)
                    self.addMortPayment(loan.name, amount, payDate, 1, period, 1)
                    num = num+1
                # print self.mortgageArray[loan[2]].transDate[-1]
            elif loan[2] > len(self.mortgageArray):
                num = 1
                payDate = 0
                while self.loanArray[loan[2]-len(self.mortgageArray)].startBalance[-1] !=0 and payDate < dateParser(endDate):
                    payDate = nextDate(startDate, period, interval*num)
                    self.addLoanPayment(loan.name, amount, payDate, 1, period, 1)
                    num = num+1
                # print self.loanArray[loan[2]-len(self.mortgageArray)].transDate[-1]

    def print_Balance(self, endDate):
        procEndDate = dateParser(endDate)
        del_buffer = 0
        for index in range(len(self.balance)-1, 0, -1):
            if self.balance[index][0] > procEndDate:
                    del_buffer = index
        # print del_buffer
        self.procBalance = self.balance[:del_buffer]

        #print headings
        print('Date'.ljust(13), ' ', end=" "),
        print('Description'.ljust(33), ' ', end=" "),
        print('Balance'.ljust(14), ' ', end=" "),
        print('Transaction Amt.'.ljust(9), ' ', end=" "),
        print()

        print(''.ljust(13, '-'), ' ', end=" ")
        print(''.ljust(33, '-'), ' ', end=" ")
        print(''.ljust(14, '-'), ' ', end=" ")
        print(''.ljust(9, '-'), ' ', end=" ")
        print()


        for index in range(0,len(self.procBalance)):
            print (self.procBalance[index][0].strftime("%d %b %Y").ljust(15), end=" "),
            print (self.procBalance[index][1].ljust(35), end=" "),
            print ("$" + str(round(self.procBalance[index][2], 2)).ljust(15), end=" "),
            print ("$" + str(round(self.procBalance[index][3], 2)).ljust(10))

        # return self.procBalance

    # def print_summary(self):
    #     print
    #     print
    #     print "Amortization Table",
    #     if hasattr(self, 'name'):
    #         print " for: %s"%self.name
    #     else:
    #         print
    #     #TODO: Fix start date for first date of payment, in case there are payments before the real start date
    #     print 'Start Date:\t\t\t%s %s %s'%(self.transDate[0].year, self.transDate[0].month, self.transDate[0].day),
    #     print '\t\tEnd Date:\t\t\t\t%s %s %s'%(self.transDate[-1].year, self.transDate[-1].month, self.transDate[-1].day)
    #     print 'Initial Balance:\t$',; print '{0:,.2f}'.format( self.startBalance[0] ),
    #     print '\tAnnual Interest:\t\t\t',; print '{0:,.2f}'.format( self.rate ),; print '%'
    #     print 'Net Payments:\t\t$',; print '{0:,.2f}'.format( sum(self.payment) ),
    #     print '\tNet Markup on Principal:\t',; print '{0:,.2f}'.format( (sum(self.payment)/self.startBalance[0] -1)*100 ),
    #     print '%'
    #     print 'Net Interest Paid:\t$',; print '{0:,.2f}'.format( sum(self.iPayment) )
    #     print
    #
    # def print_info(self):
    #     #Print Title
    #     self.print_summary()
    #     # Print headers
    #     print 'Pmt no'.rjust(6), ' ',
    #     print 'Date'.ljust(13), ' ',
    #     print 'Balance'.ljust(13), ' ',
    #     print 'Payment'.ljust(13), ' ',
    #     print 'Principal'.ljust(13), ' ',
    #     print 'Interest'.ljust(13), ' ',
    #     print 'End Balance'.ljust(13), ' ',
    #     print
    #
    #     print ''.rjust(6, '-'), ' ',
    #     print ''.rjust(13, '-'), ' ',
    #     print ''.ljust(13, '-'), ' ',
    #     print ''.rjust(13, '-'), ' ',
    #     print ''.ljust(13, '-'), ' ',
    #     print ''.rjust(13, '-'), ' ',
    #     print ''.rjust(13, '-'), ' '
    #     print
    #     # Print data
    #     # Print data
    #     for num in range(0, len(self.startBalance)):
    #
    #         print str(num+1).center(6), ' ',
    #         print '{0:s}'.format(self.transDate[num].strftime("%d %b %Y")).rjust(13), ' ',
    #         print '{0:,.2f}'.format(self.startBalance[num]).rjust(13), ' ',
    #         print '{0:,.2f}'.format(self.payment[num]).rjust(13), ' ',
    #         print '{0:,.2f}'.format(self.pPayment[num]).rjust(13), ' ',
    #         print '{0:,.2f}'.format(self.iPayment[num]).rjust(13), ' ',
    #         print '{0:,.2f}'.format(self.endBalance[num]).rjust(13), ' '

# General transaction class, which is a super-class to loans, investments, payments, and income
class transaction:
    def __init__(self, amount, startDate, endDate, period, interval, name=None, num_times=float('inf')):
        self.num_times = num_times
        self.startDate = dateParser(startDate)
        self.endDate = dateParser(endDate)
        self.period = period
        self.interval = interval
        self.amount = amount
        if name:
            self.name = name
        else:
            self.name = "Unnamed Transaction"
        self.evaluate()

    def evaluate(self):

        fixedPayment = self.amount
        self.payment = []
        self.transDate = []
        self.num = [1]
        iteratePayment = True
        self.transDate.append(self.startDate)

        #Payment Cycle
        while iteratePayment:

            newDate = nextDate(self.startDate, self.period, self.num[-1]*self.interval)
            #print "%s\t%s\t%s\t%s"%(self.num[-1],self.interval,self.period, newDate)
            self.payment.append(fixedPayment)
            self.num.append(len(self.transDate)+1)
            self.transDate.append(newDate)


            #while loop exit conditions
            if self.num[-1] >= self.num_times or newDate > self.endDate:
                iteratePayment = False

        del self.num[-1]
        del self.transDate[-1]


class regularPayment(transaction):
    def __init__(self, amount, startDate, endDate, period, interval, name=None, num_times=float('inf')):
        #Always ensure the amount of the transaction is negative
        transaction.__init__(self, -1 * abs(amount), startDate, endDate, period, interval, name=name, num_times=num_times)


class regularIncome(transaction):
    def __init__(self, amount, startDate, endDate, period, interval, name=None, num_times=float('inf')):
        #Always ensure the amount of the transaction is negative
        transaction.__init__(self, abs(amount), startDate, endDate, period, interval, name=name, num_times=num_times)


class financing:
    #TODO:  Add deferment interval to loan as an option (services same-as-cash loans, etc)
    #TODO:  Add ability to have a pay-on date be different than the pay-due date for better accuracy in planning
    def __init__(self, principal, rate, term, startDate, period, interval, name=None):
        self.principal = principal
        self.rate = round(rate,5)
        self.term = term
        self.startDate = dateParser(startDate)
        self.period = period
        self.interval = interval
        self.adjPay=False #variable to allow adjustable payments after extra payments made
        # self.adjPay=True

        if name:
            self.name = name
        else:
            self.name = "Unnamed Loan"
        self.extra_payments = []
        self.evaluate()

    def addPayment(self, date, amount):
        paymentDate = dateParser(date)
        if amount > 0:
            self.extra_payments.append( (paymentDate, amount) )
        else:
            print ("Negative payments to loans are not allowed, payment of $%d on %s ignored"%(amount,paymentDate))
        self.extra_payments.sort()
        self.evaluate()

    def evaluate(self):
        #TODO:  Take into account if a payment is larger than the remaining balance + interest
        self.transDate = []
        self.payterm = []
        self.startBalance = []
        self.payment = []
        self.iPayment = []
        self.pPayment = []
        self.endBalance = []
        fixedPayment = round( pmt( self.principal, self.rate, self.term, self.startDate, self.period), 5)


        #Check for payments made prior to start of loan (hey, it could happen...)
        for xtrapayment in self.extra_payments:
            if xtrapayment[0] < self.startDate:

                self.transDate.append(xtrapayment[0])
                self.payterm.append(0)
                if not self.endBalance:
                    self.startBalance.append(0)
                else:
                    self.startBalance.append(self.endBalance[-1])
                self.payment.append(xtrapayment[1])
                self.iPayment.append(0)
                self.pPayment.append(xtrapayment[1])
                self.endBalance.append(self.startBalance[-1] - self.pPayment[-1])

        #First normal payment
        self.transDate.append(self.startDate)
        self.payterm.append(0)
        if not self.endBalance:
            self.startBalance.append(self.principal)
            self.payment.append(fixedPayment)
        else:
            self.startBalance.append(self.endBalance[-1])
            if self.adjPay:
                self.payment.append( round( pmt( self.endBalance[-1], self.rate, self.term - self.payterm[-1],
                                                 self.transDate[-1], self.period), 5) )
            else:
                self.payment.append( fixedPayment )
        self.iPayment.append( round( (self.startBalance[-1]) *
                                         (self.interval *
                                          (self.rate/(numPeriods( self.transDate[-1], self.period) * 100))), 5))
        #print(self.payment[-1])
        #print(self.iPayment[-1])
        #tempvar1 = self.payment[-1]
        #tempvar2 = self.iPayment[-1]
        #print(self.startBalance[-1] - self.pPayment[-1])

        self.pPayment.append( self.payment[-1] - Decimal(self.iPayment[-1]))
        #self.pPayment.append(tempvar1 - Decimal(tempvar2))
        self.endBalance.append(Decimal(self.startBalance[-1]) - self.pPayment[-1])

        while self.endBalance[-1] > 0.01:

            for xtrapayment in self.extra_payments:

                # print "%s\t%s\t%s\t%s"%(xtrapayment[0],
                #                 nextDate(self.startDate, self.period, self.payterm[-1]),
                #                 nextDate(self.startDate, self.period, self.payterm[-1]+1),
                #                 xtrapayment[0] > nextDate(self.startDate, self.period, self.payterm[-1]) and \
                #                 xtrapayment[0] <= nextDate(self.startDate, self.period, self.payterm[-1]+1))


                if xtrapayment[0] > nextDate(self.startDate, self.period, self.payterm[-1]) and \
                   xtrapayment[0] <= nextDate(self.startDate, self.period, self.payterm[-1]+1):
                    self.transDate.append(xtrapayment[0])
                    self.payterm.append(self.payterm[-1])
                    if not self.endBalance:
                        self.startBalance.append(0)
                    else:
                        self.startBalance.append(self.endBalance[-1])
                    self.payment.append(xtrapayment[1])
                    self.iPayment.append(0)
                    self.pPayment.append(xtrapayment[1])
                    self.endBalance.append(self.startBalance[-1] - self.pPayment[-1])


            # print "%s\t%s"%(self.transDate[-1], self.payterm[-1])
            self.payterm.append(self.payterm[-1] + 1)
            self.transDate.append( nextDate(self.startDate, self.period, self.payterm[-1]) )

            if not self.endBalance:
                self.startBalance.append(self.principal)
                self.payment.append(fixedPayment)
            else:
                self.startBalance.append(self.endBalance[-1])
                if self.adjPay:
                    self.payment.append( round( pmt( self.startBalance[-1], self.rate, self.term - self.payterm[-1],
                                                     self.transDate[-1], self.period), 5) )
                else:
                    self.payment.append( fixedPayment )
            self.iPayment.append( round( (self.startBalance[-1]) *
                                             (self.interval *
                                              (Decimal(self.rate)/(numPeriods( self.transDate[-1], self.period) * Decimal(100)))), 5))
            self.pPayment.append( self.payment[-1] - self.iPayment[-1])
            self.endBalance.append( round(self.startBalance[-1] - self.pPayment[-1], 5))
            # print self.endBalance[-1]

        self.sign_correct()

    def sign_correct(self):
        tempPayment = [ -1 * abs(entry) for entry in self.payment]
        self.payment = tempPayment
        tempIPayment = [ -1 * abs(entry) for entry in self.iPayment]
        self.iPayment = tempIPayment
        tempBalance = [ -1 * abs(entry) for entry in self.startBalance]
        self.startBalance = tempBalance
        tempEndBalance = [ -1 * abs(entry) for entry in self.endBalance]
        self.endBalance = tempEndBalance

    def print_summary(self):
        print()
        print()
        print ("Amortization Table"),
        if hasattr(self, 'name'):
            print (" for: %s"%self.name)
        else:
            print()
        #TODO: Fix start date for first date of payment, in case there are payments before the real start date
        print ('Start Date:\t\t\t%s %s %s'%(self.transDate[0].year, self.transDate[0].month, self.transDate[0].day), end=" "),
        print ('\t\tEnd Date:\t\t\t\t%s %s %s'%(self.transDate[-1].year, self.transDate[-1].month, self.transDate[-1].day))
        print ('Initial Balance:\t$', end=" "),
        print ('{0:,.2f}'.format( self.startBalance[0] ), end=" "),
        print ('\tAnnual Interest:\t\t\t', end=" "),
        print ('{0:,.2f}'.format( self.rate ), end=" "),
        print ('%')
        print ('Net Payments:\t\t$', end=" "),
        print ('{0:,.2f}'.format( sum(self.payment) ), end=" ")
        print ('\tNet Markup on Principal:\t', end=" "),
        print ('{0:,.2f}'.format( (sum(self.payment)/self.startBalance[0] -1)*100 ), end=" "),
        print ('%')
        print ('Net Interest Paid:\t$', end=" "),
        print ('{0:,.2f}'.format( sum(self.iPayment) ))
        print ()

    def print_info(self):
        #Print Title
        self.print_summary()
        # Print headers
        print ('Pmt no'.rjust(6), ' ', end=" "),
        print ('Date'.ljust(13), ' ', end=" "),
        print ('Balance'.ljust(13), ' ', end=" "),
        print ('Payment'.ljust(13), ' ', end=" "),
        print ('Principal'.ljust(13), ' ', end=" "),
        print ('Interest'.ljust(13), ' ', end=" "),
        print ('End Balance'.ljust(13), ' ', end=" "),
        print()

        print (''.rjust(6, '-'), ' ', end=" "),
        print (''.rjust(13, '-'), ' ', end=" "),
        print (''.ljust(13, '-'), ' ', end=" "),
        print (''.rjust(13, '-'), ' ', end=" "),
        print (''.ljust(13, '-'), ' ', end=" "),
        print (''.rjust(13, '-'), ' ', end=" "),
        print (''.rjust(13, '-'), ' ')
        print()
        # Print data
        # Print data
        for num in range(0, len(self.startBalance)):

            print (str(num+1).center(6), ' ', end=" "),
            print ('{0:s}'.format(self.transDate[num].strftime("%d %b %Y")).rjust(13), ' ', end=" "),
            print ('{0:,.2f}'.format(self.startBalance[num]).rjust(13), ' ', end=" "),
            print ('{0:,.2f}'.format(self.payment[num]).rjust(13), ' ', end=" "),
            print ('{0:,.2f}'.format(self.pPayment[num]).rjust(13), ' ', end=" "),
            print ('{0:,.2f}'.format(self.iPayment[num]).rjust(13), ' ', end=" "),
            print ('{0:,.2f}'.format(self.endBalance[num]).rjust(13), ' ')


class investment:
    def __init__(self, principal, rate, term, startDate, endDate, period, interval, name=None):
        self.principal = principal
        self.rate = rate
        self.term = term
        self.startDate = dateParser(startDate)
        self.endDate = dateParser(endDate)
        self.period = period
        self.interval = interval
        if isinstance(name, str):
            self.name = name
        else:
            self.name = "Unnamed Investment"
        self.iterateFlag = True
        self.interest = []
        self.balance = []
        self.transDate = []

        self.transDate.append(self.startDate)
        self.balance.append(principal)

        self.num = []
        self.num.append(0)
        self.evaluate()

    def evaluate(self):
        iterateFlag = True
        while self.iterateFlag:
            next_Date = nextDate(self.transDate[-1], self.period, self.interval)
            if self.num[-1] >= self.term or next_Date > self.endDate:
                self.iterateFlag = False
            self.transDate.append(next_Date)
            self.interest.append( round( (self.balance[-1]) *
                                         (self.interval *
                                          (self.rate/(numPeriods( self.transDate[-1], self.period) * 100))), 5))
            self.balance.append(self.balance[-1] + self.interest[-1])
            self.num.append(self.num[-1]+1)


class loan(financing):
    def __init__(self, principal, rate, term, startDate, period, interval, name=None):
        financing.__init__(self, abs(principal), rate, term, startDate, period, interval, name=name)


#If this code is run by itself (not called or included, then run the following:
if __name__ == "__main__" or __name__ == "__builtin__":

    #Welcome to the financial calculator!

    #Create a porfolio object, startDate is optional
    demo_Port = Portfolio("Demonstration Portfolio", startDate="03/01/2014")

    #Create a mortgage.  Mortgage's and loans are different in that mortgage principals accrue as assets
    demo_Port.addMortgage(250000, 3.25, 30*12, '04/01/2012', 'm', 1, name="Home Loan")
    #Make an advanced payment on the mortgage
    demo_Port.addMortPayment("Home Loan", 10000, "02/15/2015", 10, 'a', 1)
    #TODO:  Create a refinancing script (pays off one loan, makes a new one in its place)

    #Create a few car loans
    demo_Port.addLoan(5500, 3.79, 2*12, "06/09/2014", 'm', 1, name="Car Loan1")
    demo_Port.addLoan(15528.66, 4.64, 60, "07/14/2014", 'm', 1, name="Car Loan2")


    # Let's pile on some student loans
    demo_Port.addLoan(2500, 3.0, 81, "02/28/2015", 'm', 1, name="Student Loan 1")
    demo_Port.addLoan(2500, 5, 81, "02/28/2015", 'm', 1, name="Student Loan 2")
    demo_Port.addLoan(5000, 7.0, 81, "02/28/2015", 'm', 1, name="Student Loan 3")

    # Create monthly expenses
    demo_Port.addExpense(150, "2/15/2015", "3/15/2042", 'm', 1, name="Energy Bill")
    demo_Port.addExpense(25, "1/01/2015", "3/15/2042", 'm', 4, name="Water Bill")
    demo_Port.addExpense(100, "01/26/2015", "01/26/2042", 'm', 1, name="Cable+Internet Bill")
    demo_Port.addExpense(105, "01/01/2015", "01/01/2042", 'w', 1, name="Groceries")
    demo_Port.addExpense(55, "01/01/2015", "01/01/2042", 'w', 1, name="Gasoline")

    # Add extra mortgage related expenses
    #TODO:  Add ability to have conditional payments, so the MIP below goes away when 20% of principal on house is paid
    demo_Port.addExpense(648, '06/1/2012', "3/15/2025", 'm', 1, name="MIP + Home Escrow")

    # Add income
    demo_Port.addIncome(2000, "2/21/2015", "3/15/2042", 'w', 2, name="Salary Income")
    demo_Port.addIncome(10000, "2/15/2015", "2/15/2042", 'a', 1, name="Tax Refund")

    # Add a milestone, which is a date from which all balances will be evaluated
    demo_Port.addMilestone("3/1/2015", 9700)

    # Print the balance up to the date below
    demo_Port.print_Balance("01/01/2020")

    #print the amortization table of the student loans
    #for loan in demo_Port.loanArray:
    #    loan.print_info()
    # for mort in demo_Port.mortgageArray:
    #     mort.print_info()

    # loan = demo_Port.loanDef["Student Loan 2"]
    # demo_Port.loanArray[loan].print_info()

    #TODO:  Fix the debt snowball so that it actually works.
    # Debt snowball takes a lump sum amount at the given interval and contributes it to your debts, starting with
    # the highest interest rate loan to the lowest.
    #TODO: include multiple debt payoff priority schemes, as well as having a user defind priority
    # demo_Port.debtSnowball(1000, "3/1/2015", "3/1/2017", 'm', 1)