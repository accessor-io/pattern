javascript:(function(){
    if(window.betBot){
        betBot.stop();
        document.querySelector('#betControls')?.remove();
        window.betBot=null;
    }

    const s=document.createElement('script');
    s.textContent=`
    const betBot={
        config:{
            baseBet: 0.0000001,
            maxBet: 0.00001,
            minBet: 0.0000001,
            betDelay: 0,
            maxLossStreak: 4,
            predictionThreshold: 0.65,
            historySize: 200,
            minPatternOccurrences: 8,
            patternMaxLength: 7,
            adaptiveThreshold: true,
            useMultiplierPatterns: true,
            timeWindowMinutes: 30,
            bayesianPriorAlpha: 1,
            bayesianPriorBeta: 1,
            reinforcementLearningRate: 0.1,
            discountFactor: 0.95,
            targetMultiplier: 2.0
        },
        state:{
            running: false,
            currentBet: 0.0000001,
            balance: 0,
            profit: 0,
            wins: 0,
            losses: 0,
            lossStreak: 0,
            lastMultiplier: 0,
            gameHistory: [],
            patterns: {},
            multiplierPatterns: {},
            lastPrediction: null,
            confidenceLevel: 0,
            adaptiveThresholdValue: 0.65,
            successfulPredictions: 0,
            totalPredictions: 0,
            bayesianProbabilities: {},
            timeSeriesData: [],
            qValues: new Map(),
            currentState: null,
            lastAction: null,
            rewardHistory: []
        },
        selectors:{
            betInput:'div.input.font-extrabold input[size="lg"]',
            betButton:'button.button.button-brand.button-m.w-full',
            balance:'.font-extrabold.ellipsis.w-0.flex-auto',
            result:'.w-full.overflow-hidden.relative.h-8.md\\\\:h-10',
            winBlock:'bg-brand_secondary',
            multiplier:'span'
        },

        validateBetAmount(amount) {
            if (!amount || amount <= 0) {
                console.warn('Invalid bet amount detected, using minimum bet');
                return this.config.minBet;
            }
            amount = Math.max(this.config.minBet, Math.min(amount, this.config.maxBet));
            return parseFloat(amount.toFixed(8));
        },

        async setBetAmount(amount){
            amount = this.validateBetAmount(amount);
            const input=document.querySelector(this.selectors.betInput);
            if(input){
                try {
                    // Focus and select all
                    input.focus();
                    input.select();
                    await new Promise(r=>setTimeout(r,50));
                    
                    // Clear the input
                    input.value='';
                    input.dispatchEvent(new Event('input',{bubbles:true}));
                    await new Promise(r=>setTimeout(r,50));
                    
                    // Set the value directly first
                    const amountStr = amount.toFixed(8);
                    input.value = amountStr;
                    input.dispatchEvent(new Event('input',{bubbles:true}));
                    await new Promise(r=>setTimeout(r,50));
                    
                    // If direct set failed, try character by character
                    if(parseFloat(input.value) === 0 || isNaN(parseFloat(input.value))) {
                        for(let i = 0; i < amountStr.length; i++) {
                            input.value = amountStr.substring(0, i + 1);
                            input.dispatchEvent(new Event('input',{bubbles:true}));
                            await new Promise(r=>setTimeout(r,10));
                        }
                    }
                    
                    // Final verification and commit
                    input.dispatchEvent(new Event('change',{bubbles:true}));
                    await new Promise(r=>setTimeout(r,50));
                    
                    // One last check
                    if(parseFloat(input.value) === 0 || isNaN(parseFloat(input.value))) {
                        console.warn('Final retry for bet amount...');
                        input.value = amountStr;
                        input.dispatchEvent(new Event('input',{bubbles:true}));
                        input.dispatchEvent(new Event('change',{bubbles:true}));
                        
                        // If still failed, try one more time with clipboard
                        if(parseFloat(input.value) === 0 || isNaN(parseFloat(input.value))) {
                            await navigator.clipboard.writeText(amountStr);
                            input.focus();
                            document.execCommand('paste');
                            input.dispatchEvent(new Event('input',{bubbles:true}));
                            input.dispatchEvent(new Event('change',{bubbles:true}));
                        }
                    }
                    
                    return true;
                } catch (e) {
                    console.error('Error setting bet:', e);
                    return false;
                }
            }
            return false;
        },

        init(){
            this.createControls();
            this.watchResults();
            this.updateBalance();
            setInterval(()=>this.updateBalance(),1000);
            this.setBetAmount(this.config.baseBet);
        },

        createControls(){
            const p=document.createElement('div');
            p.innerHTML='<div id="betControls" style="position:fixed;top:20px;right:20px;background:#222;padding:15px;border-radius:8px;z-index:9999;color:white;min-width:200px;box-shadow:0 0 10px rgba(0,0,0,0.5);">' +
                '<div style="margin-bottom:10px;cursor:move;padding:5px;background:#333;border-radius:4px;" id="dragHandle">⚙️ Micro-Bet ML</div>' +
                '<div style="margin-bottom:15px;">' +
                    '<button id="startBot" style="background:green;padding:8px 15px;border-radius:4px;margin-right:5px;width:70px;">Start</button>' +
                    '<button id="stopBot" style="background:#c00;padding:8px 15px;border-radius:4px;width:70px;">Stop</button>' +
                '</div>' +
                '<div style="margin-bottom:10px;">Base Bet: <input type="number" id="baseBetInput" value="' + this.config.baseBet + '" step="0.0000001" min="0.0000001" style="width:120px;background:#333;color:white;padding:4px;border-radius:4px;"></div>' +
                '<div style="margin-bottom:10px;">Speed (ms): <input type="number" id="speedInput" value="' + this.config.betDelay + '" step="200" min="0" style="width:80px;background:#333;color:white;padding:4px;border-radius:4px;"></div>' +
                '<div id="stats" style="margin-top:15px;background:#333;padding:10px;border-radius:4px;">' +
                    '<div>Balance: <span id="balanceDisplay" style="float:right;">0.00000000</span></div>' +
                    '<div>Current Bet: <span id="currentBetDisplay" style="float:right;">0.00000001</span></div>' +
                    '<div>Profit: <span id="profitDisplay" style="float:right;">0.00000000</span></div>' +
                    '<div>Win/Loss: <span id="wlDisplay" style="float:right;">0/0</span></div>' +
                    '<div>Win Rate: <span id="winRateDisplay" style="float:right;">0%</span></div>' +
                    '<div>Last Multi: <span id="multiplierDisplay" style="float:right;">0x</span></div>' +
                '</div>' +
            '</div>';
            document.body.appendChild(p);

            const controls=document.getElementById('betControls');
            const handle=document.getElementById('dragHandle');
            let isDragging=false;
            let currentX;
            let currentY;
            let initialX;
            let initialY;
            let xOffset=0;
            let yOffset=0;

            handle.addEventListener('mousedown',(e)=>{
                initialX=e.clientX-xOffset;
                initialY=e.clientY-yOffset;
                isDragging=true;
            });

            document.addEventListener('mousemove',(e)=>{
                if(isDragging){
                    e.preventDefault();
                    currentX=e.clientX-initialX;
                    currentY=e.clientY-initialY;
                    xOffset=currentX;
                    yOffset=currentY;
                    controls.style.transform='translate('+currentX+'px, '+currentY+'px)';
                }
            });

            document.addEventListener('mouseup',()=>{
                isDragging=false;
            });

            document.getElementById('startBot').onclick=()=>this.start();
            document.getElementById('stopBot').onclick=()=>this.stop();
            document.getElementById('baseBetInput').onchange=async(e)=>{
                const newBet=parseFloat(e.target.value);
                if(newBet>0){
                    this.config.baseBet=newBet;
                    this.state.currentBet=newBet;
                    await this.setBetAmount(newBet);
                }
            };
            document.getElementById('speedInput').onchange=(e)=>{
                this.config.betDelay=parseInt(e.target.value);
            };
        },

        watchResults(){
            const r=document.querySelector(this.selectors.result);
            if(r)new MutationObserver(()=>this.checkResult()).observe(r,{childList:true,subtree:true});
        },

        async start(){
            if(this.state.running)return;
            this.state.running=true;
            document.getElementById('startBot').style.background='#006400';
            await this.placeBet();
        },

        stop(){
            this.state.running=false;
            document.getElementById('startBot').style.background='green';
        },

        async placeBet(){
            if(!this.state.running)return;
            if(await this.setBetAmount(this.state.currentBet)){
                const button=document.querySelector(this.selectors.betButton);
                if(button){
                    await new Promise(r=>setTimeout(r,100));
                    button.click();
                }
            }
        },

        checkResult(){
            const blocks=document.querySelectorAll(this.selectors.result+' > div');
            if(!blocks.length)return;
            
            const last=blocks[blocks.length-1];
            const won=last.classList.contains(this.selectors.winBlock);
            const multiplierEl=last.querySelector(this.selectors.multiplier);
            const multiplier=multiplierEl?parseFloat(multiplierEl.textContent.replace('x','')):1;
            
            this.state.lastMultiplier=multiplier;
            
            if(won){
                this.state.wins++;
                this.state.profit+=this.state.currentBet*(multiplier-1);
                this.state.lossStreak=0;
                this.state.currentBet=this.config.baseBet;
            }else{
                this.state.losses++;
                this.state.profit-=this.state.currentBet;
                this.state.lossStreak++;
                if(this.state.lossStreak>=this.config.maxLossStreak){
                    this.state.currentBet=this.config.baseBet;
                    this.state.lossStreak=0;
                }else{
                    this.state.currentBet=Math.min(this.state.currentBet*2,this.config.maxBet);
                }
            }

            this.updateStats();
            if(this.state.running)setTimeout(()=>this.placeBet(),this.config.betDelay);
        },

        updateBalance(){
            const b=document.querySelector(this.selectors.balance);
            if(b)this.state.balance=parseFloat(b.textContent.replace(/[^0-9.]/g,''));
            this.updateStats();
        },

        updateStats(){
            document.getElementById('balanceDisplay').textContent=this.state.balance.toFixed(8);
            document.getElementById('currentBetDisplay').textContent=this.state.currentBet.toFixed(8);
            document.getElementById('profitDisplay').textContent=this.state.profit.toFixed(8);
            document.getElementById('profitDisplay').style.color=this.state.profit>=0?'#4CAF50':'#f44336';
            document.getElementById('wlDisplay').textContent=this.state.wins+'/'+this.state.losses;
            const winRate=this.state.wins+this.state.losses>0?(this.state.wins/(this.state.wins+this.state.losses)*100).toFixed(1):'0.0';
            document.getElementById('winRateDisplay').textContent=winRate+'%';
            document.getElementById('multiplierDisplay').textContent=this.state.lastMultiplier.toFixed(2)+'x';
        }
    };

    betBot.init();`;
    document.head.appendChild(s);
})(); 