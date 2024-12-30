SUBROUTINE sumImageWithinCircle(ndiv, nx, ny, xmin, xmax, ymin, ymax, r, cx, cy, img, tot)
    !f2py threadsafe

    ! Import standard modules ...
    USE ISO_C_BINDING

    IMPLICIT NONE

    ! Declare inputs/outputs ...
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: ndiv
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: nx
    INTEGER(kind = C_LONG_LONG), INTENT(in)                                     :: ny
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: xmin
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: xmax
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: ymin
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: ymax
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: r
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: cx
    REAL(kind = C_DOUBLE), INTENT(in)                                           :: cy
    REAL(kind = C_DOUBLE), DIMENSION(ny, nx), INTENT(in)                        :: img
    REAL(kind = C_DOUBLE), INTENT(out)                                          :: tot

    ! Declare internal variables ...
    INTEGER(kind = C_LONG_LONG)                                                 :: ix
    INTEGER(kind = C_LONG_LONG)                                                 :: iy
    REAL(kind = C_DOUBLE)                                                       :: dx
    REAL(kind = C_DOUBLE)                                                       :: dy
    REAL(kind = C_DOUBLE)                                                       :: frac
    REAL(kind = C_DOUBLE), ALLOCATABLE, DIMENSION(:)                            :: xaxis
    REAL(kind = C_DOUBLE), ALLOCATABLE, DIMENSION(:)                            :: yaxis
    REAL(kind = C_DOUBLE), ALLOCATABLE, DIMENSION(:, :)                         :: dist

    ! Allocate arrays ...
    ! NOTE: I decided not to use "sub_allocate_array()" here so as to not add a
    !       dependency to this project.
    ALLOCATE(xaxis(nx + 1))
    ALLOCATE(yaxis(ny + 1))
    ALLOCATE(dist(ny + 1, nx + 1))

    ! Calculate size of pixels ...
    dx = (xmax - xmin) / REAL(nx, kind = C_DOUBLE)
    dy = (ymax - ymin) / REAL(ny, kind = C_DOUBLE)

    ! Initialize total ...
    tot = 0.0e0_C_DOUBLE

    !$omp parallel                                                              &
    !$omp default(none)                                                         &
    !$omp private(frac)                                                         &
    !$omp private(ix)                                                           &
    !$omp private(iy)                                                           &
    !$omp shared(cx)                                                            &
    !$omp shared(cy)                                                            &
    !$omp shared(dist)                                                          &
    !$omp shared(dx)                                                            &
    !$omp shared(dy)                                                            &
    !$omp shared(img)                                                           &
    !$omp shared(ndiv)                                                          &
    !$omp shared(nx)                                                            &
    !$omp shared(ny)                                                            &
    !$omp shared(r)                                                             &
    !$omp shared(xaxis)                                                         &
    !$omp shared(xmin)                                                          &
    !$omp shared(yaxis)                                                         &
    !$omp shared(ymin)                                                          &
    !$omp reduction(+:tot)
        !$omp do                                                                &
        !$omp schedule(dynamic)
            ! Create nodes relative to the centre of the circle ...
            DO ix = 1_C_LONG_LONG, nx + 1_C_LONG_LONG
                xaxis(ix) = xmin + REAL(ix - 1_C_LONG_LONG, kind = C_DOUBLE) * dx - cx
            END DO
        !$omp end do

        !$omp do                                                                &
        !$omp schedule(dynamic)
            ! Create nodes relative to the centre of the circle ...
            DO iy = 1_C_LONG_LONG, ny + 1_C_LONG_LONG
                yaxis(iy) = ymin + REAL(iy - 1_C_LONG_LONG, kind = C_DOUBLE) * dy - cy
            END DO
        !$omp end do

        !$omp do                                                                &
        !$omp schedule(dynamic)
            ! Find out the distance of each node to the centre of the circle ...
            DO ix = 1_C_LONG_LONG, nx + 1_C_LONG_LONG
                DO iy = 1_C_LONG_LONG, ny + 1_C_LONG_LONG
                    dist(iy, ix) = HYPOT(xaxis(ix), yaxis(iy))
                END DO
            END DO
        !$omp end do

        !$omp do                                                                &
        !$omp schedule(dynamic)
            ! Loop over x-axis ...
            DO ix = 1_C_LONG_LONG, nx
                ! Loop over y-axis ...
                DO iy = 1_C_LONG_LONG, ny
                    ! Skip this pixel if it is empty ...
                    IF(img(iy, ix) == 0.0e0_C_DOUBLE)THEN
                        CYCLE
                    END IF

                    ! Add none of this pixel if it is all outside the circle ...
                    IF(ALL(dist(iy:iy + 1_C_LONG_LONG, ix:ix + 1_C_LONG_LONG) >= r))THEN
                        CYCLE
                    END IF

                    ! Add all of this pixel if it is all within the circle ...
                    IF(ALL(dist(iy:iy + 1_C_LONG_LONG, ix:ix + 1_C_LONG_LONG) <= r))THEN
                        tot = tot + img(iy, ix)
                        CYCLE
                    END IF

                    ! Add part of this pixel ...
                    CALL findFractionOfPixelWithinCircle(                       &
                        ndiv = ndiv,                                            &
                        xmin = xaxis(ix),                                       &
                        xmax = xaxis(ix + 1_C_LONG_LONG),                       &
                        ymin = yaxis(iy),                                       &
                        ymax = yaxis(iy + 1_C_LONG_LONG),                       &
                           r = r,                                               &
                          cx = 0.0e0_C_DOUBLE,                                  &
                          cy = 0.0e0_C_DOUBLE,                                  &
                        frac = frac                                             &
                    )
                    tot = tot + img(iy, ix) * frac
                END DO
            END DO
        !$omp end do
    !$omp end parallel

    ! Clean up ...
    DEALLOCATE(xaxis)
    DEALLOCATE(yaxis)
    DEALLOCATE(dist)
END SUBROUTINE sumImageWithinCircle
