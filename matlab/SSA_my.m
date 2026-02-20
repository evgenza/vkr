function SSA_my(Y,K,d,L,R);

for k=1:R;
    y=Y(K+(k-1)*d+1:K+(k-1)*d+L,1);   %y - столбец
    s0(k)=Huang_f(y);        %минимальная разность сингулярных чисел
    y_d=diff(y,1); 
   %y_d=diff(y,2);
    y_h(k)=max(y_d)-min(y_d);    
end;
Js=find(s0<0.005);
ss=zeros(size(s0)); ss(Js)=ones(size(Js))*mean(y_h); 

hF6=figure; 
set(hF6,'Units','Normalized','Pos',[0.2 0.175 0.78 0.6],...
    'Color',[0.8 0.8 0.8]);
subplot(2,1,1);
plot(y_h,'LineWidth',4); grid; %axis([0 R 0 1]);

hold on; plot(ss,'r','LineWidth',4);

subplot(2,1,2);
plot(s0,'LineWidth',4); grid; %axis([0 R 0 1]);
title('Разности логарифмов сингулярных чисел','FontSize',14);
xlabel('Время (с)','FontSize',14); 