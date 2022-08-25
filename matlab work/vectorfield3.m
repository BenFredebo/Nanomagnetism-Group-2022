function vectorfield3(F,xval,yval,zval)
% vectorfield3([F1,F2,F3],x1:dx:x2,y1:dy:y2,z1:dz:z2)
% Plot 3D vectorfield [F1,F2,F3] for 
% using x-values from x1 to x2 with spacing of dx
%       y-values from y1 to y2 with spacing of dy
%       z-values from z1 to z2 with spacing of dz

[xg,yg,zg] = meshgrid(xval,yval,zval);      % values x,y,z on a grid
F1f = inline(vectorize(F(1)),'x','y','z');
F2f = inline(vectorize(F(2)),'x','y','z');
F3f = inline(vectorize(F(3)),'x','y','z');
F1g = F1f(xg,yg,zg);   % values of F1 on this grid
F2g = F2f(xg,yg,zg);   % values of F1 on this grid
F3g = F3f(xg,yg,zg);   % values of F1 on this grid
newplot

% hc = coneplot(xg,yg,zg,F1g,F2g,F3g,xg,yg,zg,0.8);
% set(hc,'FaceColor','red','EdgeColor','none')

hc = coneplot(xg,yg,zg,F1g,F2g,F3g,xg,yg,zg,zg,0.8);
set(hc,'EdgeColor','none')

set(hc,'DiffuseStrength',.8) 
view(3); 
lighting gouraud