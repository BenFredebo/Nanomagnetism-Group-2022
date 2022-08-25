function [Hy] = polarfield(a,b,X,Y,I)
    %a is half of stripline length in nanometers
    %b is half of stripline height in nanometers
    %X is relative x position (centred at 0,0 on the stripline)
    %Y is relative Y position (centred at 0,0 on the stripline)
    %I is current value in amps
    %Returns polar magnetic field component Hy

    p=pi;
    Hy = (I/(8*p*a*b))* ...
        (((b-Y)* ...
        (((1/2)*log(((b-Y)^2 + (a-X)^2)/((b-Y)^2+(-a-X)^2))) ...
        + ((a-X)/(b-Y))*atan((b-Y)/(a-X)) ...
        -((-a-X)/(b-Y))*atan((b-Y)/(-a-X)))) ...
        -((-b-Y)* ... %potentially +
        ((1/2)*log(((a-X)^2 + (-b-Y)^2)/((-a-X)^2+(-b-Y)^2)) ...
        + ((a-X)/(-b-Y))*atan((-b-Y)/(a-X)) ...
        -((-a-X)/(-b-Y))*atan((-b-Y)/(-a-X)))));
end
