function specgram_my(Y);

hF5=figure; 
set(hF5,'Units','Norm','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
[S,F,T]=spectrogram(Y,32,30,1024,1);
    F1=F(1:64); S1=S(1:64,:); 
    mesh(T,F1,abs(S1));  box on;  view(-45,65);
        
ylabel('×àñòîòà (Ãö)','FontName','Courier New Cyr',...
    'FontSize',14,'FontWeight','Bold');
xlabel('Âðåìÿ (ñ)','FontName','Courier New Cyr',...
    'FontSize',14,'FontWeight','Bold');
zlabel('ÑÏÌ (ìÂ)','FontName','Courier New Cyr',...
    'FontSize',14,'FontWeight','Bold');
axis([0 4000 0 0.06 0 max(max(abs(S1)))])   
    
    
