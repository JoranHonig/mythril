contract Rubixi {

        //Declare variables for storage critical to contract
        uint private balance = 0;
        uint private collectedFees = 0;
        uint private feePercent = 10;
        uint private pyramidMultiplier = 300;
        uint private payoutOrder = 0;

        address private creator;

        //Sets creator
        function DynamicPyramid() {
                creator = msg.sender;
        }

        modifier onlyowner {
                if (msg.sender == creator) _;
        }

        struct Participant {
                address etherAddress;
                uint payout;
        }

        Participant[] private participants;

        //Fallback function
        function() payable {
            init();
        }

        //init function run on fallback
        function init() private {
                //Ensures only tx with value of 1 ether or greater are processed and added to pyramid
                if (msg.value < 1 ether) {
                        collectedFees += msg.value;
                        return;
                }

                uint _fee = feePercent;
                //50% fee rebate on any ether value of 50 or greater
                if (msg.value >= 50 ether) _fee /= 2;

                addPayout(_fee);
        }

        //Function called for valid tx to the contract
        function addPayout(uint _fee) private {
                //Adds new address to participant array
                participants.push(Participant(msg.sender, (msg.value * pyramidMultiplier) / 100));

                //These statements ensure a quicker payout system to later pyramid entrants, so the pyramid has a longer lifespan
                if (participants.length == 10) pyramidMultiplier = 200;
                else if (participants.length == 25) pyramidMultiplier = 150;

                // collect fees and update contract balance
                balance += (msg.value * (100 - _fee)) / 100;
                collectedFees += (msg.value * _fee) / 100;

                //Pays earlier participiants if balance sufficient
                while (balance > participants[payoutOrder].payout) {
                        uint payoutToSend = participants[payoutOrder].payout;
                        participants[payoutOrder].etherAddress.send(payoutToSend);

                        balance -= participants[payoutOrder].payout;
                        payoutOrder += 1;
                }
        }

        //Fee functions for creator
        function collectAllFees() onlyowner {
                if (collectedFees == 0) throw;

                creator.send(collectedFees);
                collectedFees = 0;
        }

}
