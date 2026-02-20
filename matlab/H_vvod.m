L=str2num(get(LL,'String'));    %ширина окна
K=str2num(get(KK,'String'));    %начало отсчёта
d=str2num(get(dd,'String'));    %сдвиг окна
m=str2num(get(mm,'String'));    %число полос для критерия Гёльдера
D=str2num(get(DD,'String'));    %отклонение для критерия Гёльдера
R=str2num(get(RR,'String'));    %число окон
alp=str2num(get(ALP,'String')); %коэффициент дисконтирования при
                                %экспоненциальном сглаживании
%====Выбор файла из меню==== 
str0=get(hmenu,'String');
v0=get(hmenu,'Value');
FName=str0{v0}; pos=findstr(FName,'.'); 
xName=char(FName(1:pos-1));
ext=char(FName(pos+1:pos+3));
if strcmp(ext,'wav')==1;
     XName=[path_my,xName];
%    X=audioread(char(XName));
     Y=wavread(char(XName));
else
     eval(['load ',path_my,xName ,',','Y']);   
end;

hF2=figure; 
set(hF2,'Units','Normalized','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
plot(Y,'LineWidth',3); grid;   axis([0 L*R min(Y) max(Y)]);
N=length(Y);
axis([0 N min(Y) max(Y)]);
Y_sm=exp_smooth_twice(Y,alp);
hold on; plot(Y_sm,'k','LineWidth',3);

title('Временной ряд данных и его тренд','FontName',...
    'Courier New Cyr','FontSize',14,'FontWeight','Bold');
xlabel('Время (с)','FontName','Courier New Cyr','FontSize',14,'FontWeight','Bold');
ylabel('Сигнал (мВ)','FontName','Courier New Cyr','FontSize',14,'FontWeight','Bold'); 


