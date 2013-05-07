! qinit routine for parabolic bowl problem, only single layer
subroutine qinit(maxmx,maxmy,meqn,mbc,mx,my,xlower,ylower,dx,dy,q,maux,aux)

    use geoclaw_module, only: grav

    implicit none

    ! Subroutine arguments
    integer, intent(in) :: maxmx,maxmy,meqn,mbc,mx,my,maux
    real(kind=8), intent(in) :: xlower,ylower,dx,dy
    real(kind=8), intent(inout) :: q(meqn,1-mbc:maxmx+mbc,1-mbc:maxmy+mbc)
    real(kind=8), intent(inout) :: aux(maux,1-mbc:maxmx+mbc,1-mbc:maxmy+mbc)

    ! Other storage
    integer :: i,j
    real(kind=8) :: x, y, eta
    real(kind=8), parameter :: x0 = 30.d3
    real(kind=8), parameter :: y0 = 21.d3 
    real(kind=8), parameter :: sigma = 1d3
    real(kind=8), parameter :: A= 1.d0
    
    do i=1-mbc,mx+mbc
        x = xlower + (i - 0.5d0)*dx
        do j=1-mbc,my+mbc
            y = ylower + (j - 0.5d0) * dx
            eta = A * exp(-((x - x0)**2 + (y - y0)**2) / sigma**2)
            q(1,i,j) = max(0.d0,eta - aux(1,i,j))
            q(2,i,j) = 0.d0
            q(3,i,j) = 0.d0
        enddo
    enddo    
end subroutine qinit
