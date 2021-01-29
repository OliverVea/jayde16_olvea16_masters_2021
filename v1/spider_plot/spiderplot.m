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

all_features=["Chimney","Manhole Cover","Mast (light fixture)","Downspout Grille","Tree","Building","Fence","Bushes","Lake","Edge of stream","Chicane"]

%% Count number of existing features in all areas

area_features = zeros(length(areas), length(all_features));

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

%% Create Spiderplot

spider(area_features.', "Spider Plot Areas", [], all_features,{'Harbor' 'Park' 'SDU' 'Suburb'});

%%
