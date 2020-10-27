clc; clear;
opts = detectImportOptions('data/Harbor_Data_Analysis.csv');
opts.ExtraColumnsRule = 'ignore';
opts.VariableNamingRule = 'preserve';
opts.SelectedVariableNames = opts.SelectedVariableNames([1:6,8:12]);
harbor = readtable('data/Harbor_Data_Analysis.csv', opts);
park = readtable('data/Park_Data_Analysis.csv', opts);
sdu = readtable('data/SDU_Data_Analysis.csv', opts);
suburb = readtable('data/Suburb_Data_Analysis.csv', opts);
%% Initialize arrays and find all features
areas = ["harbor", "park", "sdu", "suburb"];

all_areas = [harbor;park;sdu;suburb];

all_features = [];

for i = 1:height(all_areas)
    if ~ismember(all_areas.('English'){i}, all_features)
        all_features = [all_features, convertCharsToStrings(all_areas.('English'){i})];
    end
end

area_features = zeros(length(areas), length(all_features));


%% Count number of existing features in all areas

for i = 1:length(areas)
    j = 1;
    for ft_name = convertCharsToStrings(eval(areas(i)).("English")).'
        if ismember(convertCharsToStrings(eval(areas(i)).("Category"){j}), ["True Positive", "False Negative"])
            ft_index = find(all_features==ft_name);
            area_features(i, ft_index) = area_features(i, ft_index) + 1;
        end
        j = j + 1;
    end
end

area_features

%% Setup data for spider plot

spider(area_features.', "Spider Plot Areas", [], all_features,{'Harbor' 'Park' 'SDU' 'Suburb'});



% create a spider plot for ranking the data
% function [f, ca, o] = spider(data,tle,rng,lbl,leg,f)
%
% inputs  6 - 5 optional
% data    input data (NxM) (# axes (M) x # data sets (N))     class real
% tle     spider plot title                                   class char
% rng     peak range of the data (Mx1 or Mx2)                 class real
% lbl     cell vector axes names (Mxq) in [name unit] pairs   class cell
% leg     data set legend identification (1xN)                class cell
% f       figure handle or plot handle                        class real
%
% outptus 3 - 3 optional
% f       figure handle                                       class integer
% x       axes handle                                         class real
% o       series object handles                               class real
%
% michael arant - jan 30, 2008
%
% to skip any parameter, enter null []
% 
% examples
% 
%  	spider([1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15;16 17 18; ...
%  	19 20 21; 22 23 24; 25 26 27]','test plot');
% 
%  	spider([1 2 3 4; 4 5 6 7; 7 8 9 10; 10 11 12 13; 13 14 15 16; ...
%  	16 17 18 19; 19 20 21 22; 22 23 24 25; 25 26 27 28],'test plot', ...
%  	[[0:3:24]' [5:3:29]'],[],{'Case 1' 'Case 2' 'Case 3' 'Case 4'});
% 
%  	spider([1 2 3 4; 4 5 6 7; 7 8 9 10; 10 11 12 13; 13 14 15 16; ...
%  	16 17 18 19; 19 20 21 22; 22 23 24 25; 25 26 27 28],'test plot', ...
%  	[],[],{'Case 1' 'Case 2' 'Case 3' 'Case 4'});
%
% 	figure; clf; set(gcf,'color','w'); s = zeros(1,4);
%  	for ii = 1:4; s(ii) = subplot(2,2,ii); end
%  	 
%  	spider([1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15;16 17 18; ...
%  	19 20 21; 22 23 24; 25 26 27]','test plot 1',[],[],[],s(1));
% 
% 	spider([1 2 3; 4 5 6; 7 8 9; 10 11 12; 13 14 15;16 17 18; ...
%  	19 20 21; 22 23 24; 25 26 27],'test plot 2',[0 30],[],[],s(2));
% 
%  	spider([1 2 3 4; 4 5 6 7; 7 8 9 10; 10 11 12 13; 13 14 15 16; ...
%  	16 17 18 19; 19 20 21 22; 22 23 24 25; 25 26 27 28]','test plot 3', ...
% 	[0 30],{'Label 1' 'Unit 1'; 'Label 2' 'Unit 2'; 'Label 3' 'Unit 3'; ...
%  	'Label 4' 'Unit 4'},{'Case 1' 'Case 2' 'Case 3' 'Case 4' 'Case 5' ...
%  	'Case 6' 'Case 7' 'Case 8' 'Case 9'},s(3));
% 
%  	spider([1 2 3 4; 4 5 6 7; 7 8 9 10; 10 11 12 13; 13 14 15 16; ...
%  	16 17 18 19; 19 20 21 22; 22 23 24 25; 25 26 27 28],'test plot 4', ...
%  	[[0:3:24]' [5:3:29]'],[],{'Case 1' 'Case 2' 'Case 3' 'Case 4'},s(4));
