%
% Created on wed Jun 1 11:43:51 2022
%
% @author: BRasmussen
%
% Script to calculate topological density of given input magnetization
% layer for specific magnetization orientation.


% First need to load in data and split into components:

% Filename on current path:

Filename = "skyrmiondata.txt"; % change this depending on wanted input
data = importdata(Filename);

% If data has multiple layers, the following can be used to configure
% the desired truncation: 


datalayer = "Layer 4" ;  %Input string is used below 

% following code depends on size of file. Assuming that the data structure
% is a n x n grid with four layers:

% In this case n = 128 but can easily be changed

nn = 128;


if datalayer=="Layer 1"            %strings can be changed for num of layers
    layerdata = data(1:(nn^2),:);

elseif datalayer == "Layer 2"
    layerdata = data((nn^2 + 1):(2*nn^2),:);

elseif datalayer == "Layer 3"
    layerdata = data((2*nn^2+1):(3*nn^2),:);

elseif datalayer == "Layer 4"
    layerdata = data((3*nn^2+1):(4*nn^2),:);
end



%splits data into components for easier comprehension

X = layerdata(:,1); Y = layerdata(:,2); Z = layerdata(:,3);
Mx = layerdata(:,4); My = layerdata(:,5); Mz = layerdata(:,6);


% Using the topological density function at end of script we can now
% get our desired dataset. The output layer will be n x n corresponding to
% the n x n X-Y plane grid from the input data:

[TopDense, skyrnum] = topologicaldensity(X,Y,Z,Mx,My,Mz);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Following code can be used to visualize the topological density data as
% well as local averages of the magnetization components in the X-Y plane
%
% plottable matrices for the above variables:

Mxplot = reshape(Mx,128,128); Myplot = reshape(My,128,128);
Mzplot = reshape(Mz,128,128); Xplot = reshape(X,128,128); 
Yplot = reshape(Y,128,128); Zplot = reshape(Z,128,128);


%% 
% In this section a local average of the magnetization components is
% found using a 2 dimensional convolution which is subsequently shrunk to
% the desired dimensions of the vector plot:

windowmatrix = ones(5,5)/5^2; % window size can be adjusted accordingly

convMx = conv2(Mxplot,windowmatrix,'same');
convMy = conv2(Myplot, windowmatrix, 'same');
convMz = conv2(Mzplot,windowmatrix,'same');

%Using the above we now want to shrink the matrix to the desired number of
%quiver arrows;

shrinkfactor = 4;  % must be factor of n

buffer = convMx(:,1:shrinkfactor:end) ;
Mx_reduced = buffer(1:shrinkfactor:end,:) ;

buffer = convMy(:,1:shrinkfactor:end) ;
My_reduced = buffer(1:shrinkfactor:end,:) ;

buffer = convMz(:,1:shrinkfactor:end) ;
Mz_reduced = buffer(1:shrinkfactor:end,:) ;

%now need plottable x and y vectors with the same dimension as the above
%reduced magnetization matrices:

X_reduced = X(1:shrinkfactor:end,:);
Y_reduced = Y(1:shrinkfactor:end,:);
Z_reduced = Z(1:shrinkfactor:end,:);

X_reducedplot = X_reduced(1:128/shrinkfactor);
Y_reducedplot = X_reducedplot;
Z_reducedplot = X_reducedplot;







%%
%{

% In order to plot the figure using a contour plot the following code will
% create an image:
figure()
contourf(Xplot,Yplot,TopDense, 20, "LineColor", 'none') % also just contour

% Colormap can be changed to whatever is needed:
%load('topdense2.mat')
colormap(gray)
title("Topological Density Profile for Thin Film:")
xlabel("x position")
ylabel("y position")

%}








%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This is where I have made changes!:                       



% Using the weighted density function, calculates expected value:
% This can be added to a plot simply with the plot function as long as
% markers are specified, i.e: plot(X_weight, Y_weight, '*')

[X_weight, Y_weight]=weighted_averages(X,Y,TopDense);

fprintf("Weighted X expected Value: %.5g \n", X_weight)
fprintf("Weighted Y expected Value: %.5g \n", Y_weight)






% copy the original topological density into a new matrix:

TopDense2 = TopDense;

% replace every instance where there is a zero value with NaN
% this will force the contour plot to plot white wherever there is a 
% NaN value:

TopDense2(TopDense2==0) = NaN;



% Now if we re-plot the density it will be only within the central region:

% With the addition of a point for the expected value:

figure()
contourf(Xplot,Yplot,TopDense2, 10, "LineColor", 'none'); 

colormap(gray)
title("Topological Density Profile for Thin Film:")
xlabel("x position")
ylabel("y position")

%{
hold on
plot(X_weight,Y_weight, '*', 'MarkerSize',6,...
    'MarkerEdgeColor','black',...
    'MarkerFaceColor',[1 1 1])
hold off

%}
% plots a better version with quiver plot:

% with the addition of a point for the expected value:

figure()
contourf(Xplot,Yplot,TopDense2, 7, "LineColor", 'none'); 

colormap(gray)
title("Topological Density Profile for Thin Film:")
xlabel("x position")
ylabel("y position")
% optional

hold on
quiv = quiver(X_reducedplot, Y_reducedplot, Mx_reduced,My_reduced,0.5);
quiv.Color = '[0,0,0.3]';
%{
plot(X_weight, Y_weight, 'p','MarkerSize',10,...
    'MarkerEdgeColor','black',...
    'MarkerFaceColor',[0.9 0.9 0.9])
%}
hold off
%grid on




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% FUNCTIONS:

function [TopD, Skyr] = topologicaldensity(X,Y,Z,Mx,My,Mz)
% topologicaldensity(X,Y,Z,Mx,My,Mz):
%
% Input data should have shape (n^2) x 1, where n is the number of bins
% along a specific axis. The function will only work for square datasets.
%
% TODO:
%       Extend capabilities to rectangular datasets
%
%
% The function calculates the topological density
% profile for a dynamic magnetic layer as well as the skyrmion number for
% the magnetic layer. This is done using the following formulas:
%
% topologicaldensity= N(x,y) = m . (dm/dy x dm/dx)       (1)
% skyrmionnumber = (1/4pi) * int( N(x,y) dxdy)           (2)
%
% OUTPUTS: 
%       TopD: n x n matrix of density values in the x,y plane
%       Skyr: skyrmion number for the layer (scalar)
%
% INPUTS:
%       X: (n^2) x 1, vector of x coordinates
%       Y: (n^2) x 1, vector of y coordinates    
%       (x,y correspond to grid in the plane)
%       Z: (n^2) x 1, vector of z coordinates (same value for layer)
%       Mx: (n^2) x 1, X magnetization components in line with X,Y,Z
%       My: (n^2) x 1, Y magnetization components in line with X,Y,Z
%       Mz: (n^2) x 1, Z magnetization components in line with X,Y,Z


% Useful data dimensions:

N = numel(X);
n = sqrt(N);

% The input data is better served as n x n matrices for derivatives so first
% it is reshaped accordingly:

Mxgrid = reshape(Mx,n,n); Mygrid = reshape(My,n,n);
Mzgrid = reshape(Mz,n,n); 

% Now we need the partial derivatives of all three vector components with
% respect to X and Y in the plane. We do this simply using the built in
% gradient function but a more complicated approach could be implemented.
% TODO: ??

[Mx_dx, Mx_dy] = gradient(Mxgrid);
[My_dx, My_dy] = gradient(Mygrid);
[Mz_dx, Mz_dy] = gradient(Mzgrid);

% In order to complete the requisite vector operations it is now useful to
% convert the derivative matrices back into vectors:

Mx_dx_vec = reshape(Mx_dx,N,1); Mx_dy_vec = reshape(Mx_dy,N,1);
My_dx_vec = reshape(My_dx,N,1); My_dy_vec = reshape(My_dy,N,1);
Mz_dx_vec = reshape(Mz_dx,N,1); Mz_dy_vec = reshape(Mz_dy,N,1);

% The 3 x 1 vector components of the derivatives for each point in the
% plane can now be made into n x 3 x 1 full vector field components:

total_dmdx = [Mx_dx_vec My_dx_vec Mz_dx_vec];
total_dmdy = [Mx_dy_vec My_dy_vec Mz_dy_vec];
total_m = [Mx My Mz];

% Can now take the term-by-term cross product for the above derivative
% column vectors:

crossterm = cross(total_dmdx,total_dmdy);

% We then take the term-by-term scalar product between the total
% magnetization vector and the above crossterm in order to satisfy equation
% (1):

topdens = dot(total_m', crossterm')';

% We now reshape the above vector into an n x n matrix that corresponds to
% the topological density in the X, Y plane:

TopD = reshape(topdens,128,128);


% For the skyrmion number, we simply integrate over the entire layer in X
% and Y using equation (2). A more complicated integration technique can be
% implimented here but we will just use a two dimensional trapezoid method:

% Integration in X:

partial_int = trapz(TopD);

% Integration in Y:

Skyr = trapz(partial_int) / (4*pi);
TopD = reshape(topdens,n,n);


end


function [X_weight, Y_weight]=weighted_averages(X,Y,q)
% weighted_averages(X,Y,q):
%
% input X,Y and q should all have the same shape and number of elements.
% 
% Function takes X and Y coordinates in a plane as well as the
% topological density profile in the plane calculated using the topological
% density function above and calculates a trivial average value of X and Y
% weighted with the density q.
%
% X_weight = int(X * q(X,Y) dxdy)
% Y_weight = int(Y * q(X,Y) dxdy)
%
%
% OUTPUTS: 
%       X_weight : weighted average of x values by q
%       Y_weight : weighted average of y values by q
%
% INPUTS:
%       X : (n^2) x 1, vector of x coordinates
%       Y : (n^2) x 1, vector of y coordinates    
%       (x,y correspond to grid in the plane)
%       q : n x n, matrix of topological density


% integrable x and y matrices:

Xint = reshape(X,128,128); 
Yint = reshape(Y,128,128);

% integrand for the two means:

X_integrand = Xint.*q;
Y_integrand = Yint.*q;

% weight integral for x and y:

partial_weight = trapz(q);
weight = trapz(partial_weight);

% x and y unweighted integral:

X_partial = trapz(X_integrand);
Y_partial = trapz(Y_integrand);

X_unweight = trapz(X_partial);
Y_unweight = trapz(Y_partial);

% weighted integrals:

X_weight = X_unweight/weight;
Y_weight = Y_unweight/weight;


end
