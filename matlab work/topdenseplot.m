% The following script visualises the data from a square magnetic thin film
% sample with magnetization measurements in all three spatial direction.
% Using the function:
% [TopD,Skyr] = topologicaldensity(X,Y,Z,Mx,My,Mz)
%
% % OUTPUTS: 
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
%
% We can find the topological density of the system for the given dataset.
% The input file must be an (n x n) x 6 input array which will be broken
% down into the respective components below. 
%
% We first need the data components:
%
%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Input the desired data set matrix here:

data = layerdata;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Vector components for calculation:

X = data(:,1); Y = data(:,2); Z = data(:,3);
Mx = data(:,4); My = data(:,5); Mz = data(:,6);

% Uses the function to find the topological density:

[TopD, sky] = topologicaldensity(X,Y,Z,Mx,My,Mz);



% To overlay a quiver plot of the x and y magnetization components we need
% a moving average of the vectors shrunk by a desired facotr for
% aesthetics:


shrinkfactor = 8;  % must be multiple of 4

buffer = convMx(:,1:shrinkfactor:end) ;
Mx_reduced = buffer(1:shrinkfactor:end,:) ;

buffer = convMy(:,1:shrinkfactor:end) ;
My_reduced = buffer(1:shrinkfactor:end,:) ;

buffer = convMz(:,1:shrinkfactor:end) ;
Mz_reduced = buffer(1:shrinkfactor:end,:) ;



% Now need plottable x and y vectors with the same dimension as the above
% reduced magnetization matrices:

X_reduced = X(1:shrinkfactor:end,:);
Y_reduced = Y(1:shrinkfactor:end,:);
Z_reduced = Z(1:shrinkfactor:end,:);

X_reducedplot = X_reduced(1:128/shrinkfactor);
Y_reducedplot=X_reducedplot;
Z_reducedplot=X_reducedplot;


% Plots the figure:

contourf(Xplot,Yplot,TopD, 5, "LineColor", 'none')
colormap(topdense2)
title("Topological Density Profile for Thin Film:")
xlabel("x position")
ylabel("y position")
hold on
%quiver plot can be turned off
q3 = quiver(X_reducedplot, Y_reducedplot, Mx_reduced,My_reduced,0.3);
q3.Color = '[0.2,0,0.2]';
hold off
Xtick = linspace(0,2.55e-5,10);
grid on



% For completeness, the topological density function is included below:


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
Mzgrid = reshape(Mz,n,n); Xgrid = reshape(X,n,n);
Ygrid = reshape(Y,n,n); Zgrid = reshape(Z,n,n);

% Now we need the partial derivatives of all three vector components with
% respect to X and Y in the plane. We do this simply using the built in
% gradient function but a more complicated approach could be implemented.
% TODO: ??

[Mx_dx, Mx_dy] = gradient(Mxgrid);
[My_dx, My_dy] = gradient(Mygrid);
[Mz_dx, Mz_dy] = gradient(Mzgrid);

% In order to complete the requisite vector operations it is now useful to
% convert th derivative matrices back into vectors:

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
TopD = reshape(topdens,128,128);





% In order to plot the figure using a contour plot the following code will
% create an image:


%{
contourf(Xplot,Yplot,TopD, 5, "LineColor", 'none')
colormap(topdense2)
title("Topological Density Profile for Thin Film:")
xlabel("x position")
ylabel("y position")
hold on
q3 = quiver(X_reducedplot, Y_reducedplot, Mx_reduced,My_reduced,0.3);
q3.Color = '[0.2,0,0.2]';
hold off
Xtick = linspace(0,2.55e-5,10);
grid on
%}


end







