function J=segment_my(Y,K,d,L,R);
n=length(Y);
Y1=diff(Y);                 %скорость
ss=std(abs(Y1));            %СКО 
J=find(abs(Y1)>ss*12);      JJ=size(J);   %номера скачков
Y2=zeros(size(Y1));
Y2(J)=Y1(J);

%Y3=[];
%for k=1:JJ;
%    j=J(k);
%    y=Y(j-L:j);
%    Y3=[Y3;y];
%end;

hF6=figure; 
set(hF6,'Units','Normalized','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
plot(Y2,'LineWidth',4); grid;  %axis([0 n 0 1.2]);
title('Скачки скорости','FontSize',14,'FontWeight','Bold');
xlabel('Номер окна','FontSize',12); 

